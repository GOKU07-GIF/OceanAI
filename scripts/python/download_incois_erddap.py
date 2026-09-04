"""Download and transform public INCOIS ERDDAP datasets.

This script uses INCOIS's public ERDDAP griddap service. It downloads a small
spatial/time subset as NetCDF and can transform the downloaded file to CSV or
Parquet for analytics/database ingestion.

Examples:
  python scripts/python/download_incois_erddap.py --list
  python scripts/python/download_incois_erddap.py --dataset sst --start 2026-01-01 --end 2026-01-03
  python scripts/python/download_incois_erddap.py --dataset value_added --start 2026-01-01 --end 2026-01-03 --format parquet
  python scripts/python/download_incois_erddap.py --dataset chlorophyll --start 2006-01-01 --end 2006-03-01 --format csv

Important:
  - Do not request the full archive in one call. Use small time/spatial chunks.
  - Dataset availability and coordinates can change; the script validates the
    downloaded NetCDF before conversion.
  - PFZ advisories and the operational ROMS holdings are not assumed to be
    downloadable through these ERDDAP datasets. Their access path must be
    validated separately before automation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import quote

import requests
import xarray as xr

BASE_URL = "https://erddap.incois.gov.in/erddap/griddap"
OUTPUT_DIR = Path("datasets/raw/incois")

DATASETS = {
    "sst": {
        "dataset_id": "NOAA_AVHRR_AMSR_datasets",
        "variables": ["sst"],
        "notes": "INCOIS ERDDAP Daily-OI SST product",
    },
    "value_added": {
        "dataset_id": "incois_valueadded_products_datasets",
        "variables": ["MLD", "D20", "GEO_U", "GEO_V"],
        "notes": "INCOIS value-added ocean products; includes MLD and geostrophic currents",
    },
    "chlorophyll": {
        "dataset_id": "IRS_chlorophyll_datasets",
        "variables": ["CHLOROPHYLL"],
        "notes": "IRS P4 OCM chlorophyll archive",
    },
}

DEFAULT_BBOX = (50.0, 90.0, 0.0, 25.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download a public INCOIS ERDDAP subset")
    parser.add_argument("--dataset", choices=sorted(DATASETS), help="Configured INCOIS dataset")
    parser.add_argument("--list", action="store_true", help="List configured datasets")
    parser.add_argument("--start", help="Start time, e.g. 2026-01-01T00:00:00Z")
    parser.add_argument("--end", help="End time, e.g. 2026-01-03T00:00:00Z")
    parser.add_argument("--min-lon", type=float, default=DEFAULT_BBOX[0])
    parser.add_argument("--max-lon", type=float, default=DEFAULT_BBOX[1])
    parser.add_argument("--min-lat", type=float, default=DEFAULT_BBOX[2])
    parser.add_argument("--max-lat", type=float, default=DEFAULT_BBOX[3])
    parser.add_argument("--format", choices=["nc", "csv", "parquet"], default="nc")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def build_query(config: dict, start: str, end: str, args: argparse.Namespace) -> str:
    variables = ",".join(config["variables"])
    # ERDDAP griddap accepts coordinate constraints directly in the query.
    return (
        f"{variables}"
        f"&time[({start}):1:({end})]"
        f"&latitude[({args.min_lat}):1:({args.max_lat})]"
        f"&longitude[({args.min_lon}):1:({args.max_lon})]"
    )


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=180, stream=True) as response:
        response.raise_for_status()
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def validate_dataset(path: Path) -> xr.Dataset:
    ds = xr.open_dataset(path)
    required = {"time", "latitude", "longitude"}
    missing = required - set(ds.coords)
    if missing:
        ds.close()
        raise ValueError(f"Missing required coordinates: {sorted(missing)}")
    if not ds.data_vars:
        ds.close()
        raise ValueError("Downloaded dataset contains no data variables")
    print("Validated NetCDF:")
    print(f"  dimensions: {dict(ds.sizes)}")
    print(f"  variables : {list(ds.data_vars)}")
    return ds


def flatten_to_table(ds: xr.Dataset):
    frame = ds.to_dataframe().reset_index()
    # Keep a stable, database-friendly ordering.
    preferred = ["time", "latitude", "longitude"]
    remaining = [c for c in frame.columns if c not in preferred]
    return frame[preferred + remaining]


def main() -> None:
    args = parse_args()

    if args.list:
        for alias, config in DATASETS.items():
            print(f"{alias}: {config['dataset_id']} -> {', '.join(config['variables'])}")
            print(f"  {config['notes']}")
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
    print(f"  output  : {nc_path}")

    download(url, nc_path)
    ds = validate_dataset(nc_path)

    try:
        if args.format == "nc":
            print(f"Ready: {nc_path}")
            return

        frame = flatten_to_table(ds)
        if args.format == "csv":
            out = args.output_dir / f"{stem}.csv"
            frame.to_csv(out, index=False)
        else:
            out = args.output_dir / f"{stem}.parquet"
            frame.to_parquet(out, index=False)
        print(f"Transformed: {out}")
    finally:
        ds.close()


if __name__ == "__main__":
    main()
