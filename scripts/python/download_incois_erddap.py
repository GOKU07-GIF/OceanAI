"""Download and transform public INCOIS ERDDAP datasets.

The script downloads small regional/time subsets as NetCDF and can transform
those files into a normalized long-form CSV or Parquet table.

Configured public gridded sources include INCOIS SST, value-added ocean
products, OCM chlorophyll, QuickSCAT wind fields, and monthly ARGO VAM
temperature/salinity profiles.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests
import xarray as xr

BASE_URL = "https://erddap.incois.gov.in/erddap/griddap"
OUTPUT_DIR = Path("datasets/raw/incois")

DATASETS = {
    "sst": {
        "dataset_id": "NOAA_AVHRR_AMSR_datasets",
        "variables": ["sst"],
        "dimensions": ["time", "zlev", "latitude", "longitude"],
        "fixed": {"zlev": 0.0},
        "units": {"sst": "degC"},
        "data_type": "observation",
    },
    "value_added": {
        "dataset_id": "incois_valueadded_products_datasets",
        "variables": ["MLD", "D20", "GEO_U", "GEO_V"],
        "dimensions": ["time", "latitude", "longitude"],
        "units": {
            "MLD": "m",
            "D20": "m",
            "GEO_U": "cm/s",
            "GEO_V": "cm/s",
        },
        "data_type": "observation",
    },
    "chlorophyll": {
        "dataset_id": "IRS_chlorophyll_datasets",
        "variables": ["CHLOROPHYLL"],
        "dimensions": ["time", "latitude", "longitude"],
        "units": {"CHLOROPHYLL": "mg/m3"},
        "data_type": "observation",
    },
    "quickscat": {
        "dataset_id": "incois_quickscat_daily_datasets",
        "variables": ["WIND_SPEED", "ZONAL_WIND_SPEED", "MERI_WIND_SPEED"],
        "dimensions": ["time", "latitude", "longitude"],
        "units": {
            "WIND_SPEED": "m/s",
            "ZONAL_WIND_SPEED": "m/s",
            "MERI_WIND_SPEED": "m/s",
        },
        "data_type": "observation",
    },
    "argo_vam": {
        "dataset_id": "incois_argo_mnt_VAM",
        "variables": ["TEMP", "SAL"],
        "dimensions": ["time", "ZAX", "latitude", "longitude"],
        "range": {"ZAX": (5.0, 2000.0)},
        "units": {"TEMP": "degC", "SAL": "PSU"},
        "data_type": "historical_profile",
    },
}

DEFAULT_BBOX = (50.0, 90.0, 0.0, 25.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download a public INCOIS ERDDAP subset")
    parser.add_argument("--dataset", choices=sorted(DATASETS), help="Configured dataset alias")
    parser.add_argument("--list", action="store_true", help="List configured datasets")
    parser.add_argument("--start", help="Start time, e.g. 2011-10-01T00:00:00Z")
    parser.add_argument("--end", help="End time, e.g. 2011-10-03T00:00:00Z")
    parser.add_argument("--min-lon", type=float, default=DEFAULT_BBOX[0])
    parser.add_argument("--max-lon", type=float, default=DEFAULT_BBOX[1])
    parser.add_argument("--min-lat", type=float, default=DEFAULT_BBOX[2])
    parser.add_argument("--max-lat", type=float, default=DEFAULT_BBOX[3])
    parser.add_argument("--format", choices=["nc", "csv", "parquet"], default="nc")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def constraint(dimension: str, start: str, end: str, args: argparse.Namespace, config: dict) -> str:
    if dimension == "time":
        return f"time[({start}):1:({end})]"
    if dimension == "latitude":
        return f"latitude[({args.min_lat}):1:({args.max_lat})]"
    if dimension == "longitude":
        return f"longitude[({args.min_lon}):1:({args.max_lon})]"
    fixed_value = config.get("fixed", {}).get(dimension)
    if fixed_value is not None:
        return f"{dimension}[({fixed_value}):1:({fixed_value})]"
    range_value = config.get("range", {}).get(dimension)
    if range_value is not None:
        minimum, maximum = range_value
        return f"{dimension}[({minimum}):1:({maximum})]"
    raise ValueError(f"No constraint configured for required dimension: {dimension}")


def build_query(config: dict, start: str, end: str, args: argparse.Namespace) -> str:
    variables = ",".join(config["variables"])
    dimensions = "".join(constraint(d, start, end, args, config) for d in config["dimensions"])
    return f"{variables}{dimensions}"


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=180, stream=True) as response:
        response.raise_for_status()
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def validate_dataset(path: Path, expected_variables: list[str], expected_dimensions: list[str]) -> xr.Dataset:
    ds = xr.open_dataset(path)
    missing_coords = {name for name in expected_dimensions if name not in ds.coords and name not in ds.dims}
    if missing_coords:
        ds.close()
        raise ValueError(f"Missing required coordinates/dimensions: {sorted(missing_coords)}")

    missing_variables = set(expected_variables) - set(ds.data_vars)
    if missing_variables:
        ds.close()
        raise ValueError(f"Missing requested variables: {sorted(missing_variables)}")

    if not ds.data_vars:
        ds.close()
        raise ValueError("Downloaded dataset contains no data variables")

    print("Validated NetCDF:")
    print(f"  dimensions: {dict(ds.sizes)}")
    print(f"  variables : {list(ds.data_vars)}")
    if "time" in ds.coords:
        print(f"  time      : {ds.time.min().item()} -> {ds.time.max().item()}")
    return ds


def flatten_to_ocean_table(
    ds: xr.Dataset,
    source: str,
    dataset_id: str,
    units: dict[str, str],
    data_type: str,
) -> pd.DataFrame:
    frame = ds.to_dataframe().reset_index()
    value_columns = [c for c in frame.columns if c not in {"time", "latitude", "longitude", "zlev", "ZAX"}]
    rows: list[pd.DataFrame] = []

    for variable in value_columns:
        part = frame[["time", "latitude", "longitude", variable]].copy()
        part = part.rename(columns={variable: "value"})
        part["variable"] = variable
        part["source"] = source
        part["dataset"] = dataset_id
        part["data_type"] = data_type
        part["quality_flag"] = "present"
        part = part.dropna(subset=["value"])
        rows.append(part)

    if not rows:
        raise ValueError("No non-null ocean observations found")

    result = pd.concat(rows, ignore_index=True)
    result["timestamp"] = pd.to_datetime(result.pop("time"), utc=True)
    result["unit"] = result["variable"].map(units).fillna("")

    return result[
        [
            "timestamp",
            "latitude",
            "longitude",
            "variable",
            "value",
            "unit",
            "source",
            "dataset",
            "data_type",
            "quality_flag",
        ]
    ].sort_values(["timestamp", "variable", "latitude", "longitude"])


def main() -> None:
    args = parse_args()

    if args.list:
        for alias, config in DATASETS.items():
            print(f"{alias}: {config['dataset_id']} -> {', '.join(config['variables'])}")
        return

    if not args.dataset or not args.start or not args.end:
        raise SystemExit("--dataset, --start and --end are required (or use --list)")

    config = DATASETS[args.dataset]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    query = build_query(config, args.start, args.end, args)
    encoded_query = quote(query, safe="&[]():,.+-")
    url = f"{BASE_URL}/{config['dataset_id']}.nc?{encoded_query}"

    stem = f"{args.dataset}_{args.start.replace(':', '').replace('-', '')}_{args.end.replace(':', '').replace('-', '')}"
    nc_path = args.output_dir / f"{stem}.nc"

    print("INCOIS download")
    print(f"  dataset : {config['dataset_id']}")
    print(f"  variables: {', '.join(config['variables'])}")
    print(f"  bbox    : {args.min_lon},{args.max_lon},{args.min_lat},{args.max_lat}")
    print(f"  time    : {args.start} -> {args.end}")
    print(f"  url     : {url}")

    download(url, nc_path)
    ds = validate_dataset(nc_path, config["variables"], config["dimensions"])

    try:
        if args.format == "nc":
            print(f"Ready: {nc_path}")
            return

        table = flatten_to_ocean_table(
            ds,
            source="INCOIS",
            dataset_id=config["dataset_id"],
            units=config["units"],
            data_type=config["data_type"],
        )
        out = args.output_dir / f"{stem}.{args.format}"
        if args.format == "csv":
            table.to_csv(out, index=False)
        else:
            table.to_parquet(out, index=False)
        print(f"Transformed: {out}")
        print(f"Rows: {len(table)}")
    finally:
        ds.close()


if __name__ == "__main__":
    main()
