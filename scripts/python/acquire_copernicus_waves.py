"""Acquire a small Copernicus Marine wave batch for OceanAI.

The operational global wave dataset provides 3-hourly VHM0 (significant wave
height), VTM02 (mean wave period), and VMDR (mean wave direction). The script
subsets the Indian west-coast region, converts the downloaded NetCDF directly
to OceanAI's canonical observation schema, and writes a Parquet file ready for
validation and PostgreSQL ingestion.

Copernicus credentials are resolved by the Copernicus Marine Toolbox from its
configured credentials file or the COPERNICUSMARINE_SERVICE_USERNAME and
COPERNICUSMARINE_SERVICE_PASSWORD environment variables.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

import copernicusmarine
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
DATASET_ID = "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i"
VARIABLES = ["VHM0", "VTM02", "VMDR"]
VARIABLE_MAP = {
    "VHM0": "wave_height_m",
    "VTM02": "wave_period_s",
    "VMDR": "wave_direction_deg",
}
DEFAULT_BBOX = (68.0, 78.0, 8.0, 24.0)
DEFAULT_OUTPUT_DIR = ROOT / "datasets" / "raw" / "copernicus"
DEFAULT_PROCESSED_DIR = ROOT / "datasets" / "processed" / "copernicus"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Acquire Copernicus Marine wave data for OceanAI")
    parser.add_argument("--start", help="Start datetime in UTC, e.g. 2026-09-04T00:00:00")
    parser.add_argument("--end", help="End datetime in UTC, e.g. 2026-09-05T00:00:00")
    parser.add_argument("--min-lon", type=float, default=DEFAULT_BBOX[0])
    parser.add_argument("--max-lon", type=float, default=DEFAULT_BBOX[1])
    parser.add_argument("--min-lat", type=float, default=DEFAULT_BBOX[2])
    parser.add_argument("--max-lat", type=float, default=DEFAULT_BBOX[3])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def default_window() -> tuple[str, str]:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    end = now
    start = end - timedelta(days=1)
    return start.strftime("%Y-%m-%dT%H:%M:%S"), end.strftime("%Y-%m-%dT%H:%M:%S")


def find_coord(ds: xr.Dataset, aliases: list[str]) -> str:
    names = set(ds.coords) | set(ds.dims)
    lower = {name.lower(): name for name in names}
    for alias in aliases:
        if alias.lower() in lower:
            return lower[alias.lower()]
    raise ValueError(f"Could not find coordinate; tried {aliases}")


def normalize(path: Path) -> pd.DataFrame:
    ds = xr.open_dataset(path)
    try:
        time_name = find_coord(ds, ["time"])
        lat_name = find_coord(ds, ["latitude", "lat"])
        lon_name = find_coord(ds, ["longitude", "lon"])

        missing = [v for v in VARIABLES if v not in ds.data_vars]
        if missing:
            raise ValueError(f"Missing requested wave variables: {missing}")

        frame = ds[VARIABLES].to_dataframe().reset_index()
        rows: list[pd.DataFrame] = []
        for provider_name in VARIABLES:
            part = frame[[time_name, lat_name, lon_name, provider_name]].copy()
            part = part.rename(
                columns={
                    time_name: "timestamp",
                    lat_name: "latitude",
                    lon_name: "longitude",
                    provider_name: "value",
                }
            )
            part = part.dropna(subset=["value"])
            if part.empty:
                continue
            part["variable"] = VARIABLE_MAP[provider_name]
            part["source"] = "Copernicus"
            part["dataset"] = DATASET_ID
            part["data_type"] = "forecast"
            part["quality_flag"] = "present"
            part["unit"] = str(ds[provider_name].attrs.get("units", ""))
            part["depth_m"] = pd.NA
            rows.append(part)

        if not rows:
            raise ValueError("No non-null wave observations found")

        result = pd.concat(rows, ignore_index=True)
        result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True, errors="coerce")
        if result["timestamp"].isna().any():
            raise ValueError("One or more wave timestamps could not be normalized")

        return result[
            [
                "timestamp",
                "latitude",
                "longitude",
                "depth_m",
                "variable",
                "value",
                "unit",
                "source",
                "dataset",
                "data_type",
                "quality_flag",
            ]
        ].sort_values(["timestamp", "variable", "latitude", "longitude"])
    finally:
        ds.close()


def main() -> None:
    args = parse_args()
    default_start, default_end = default_window()
    start = args.start or default_start
    end = args.end or default_end

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.processed_dir.mkdir(parents=True, exist_ok=True)

    stem = f"waves_{start.replace(':', '').replace('-', '')}_{end.replace(':', '').replace('-', '')}"
    nc_path = args.output_dir / f"{stem}.nc"
    parquet_path = args.processed_dir / f"{stem}.parquet"

    print("Copernicus Marine waves")
    print(f"  dataset : {DATASET_ID}")
    print(f"  variables: {', '.join(VARIABLES)}")
    print(f"  bbox    : {args.min_lon},{args.max_lon},{args.min_lat},{args.max_lat}")
    print(f"  time    : {start} -> {end}")
    print(f"  raw     : {nc_path}")
    print(f"  processed: {parquet_path}")

    request = {
        "dataset_id": DATASET_ID,
        "variables": VARIABLES,
        "minimum_longitude": args.min_lon,
        "maximum_longitude": args.max_lon,
        "minimum_latitude": args.min_lat,
        "maximum_latitude": args.max_lat,
        "start_datetime": start,
        "end_datetime": end,
        "output_filename": nc_path.name,
        "output_directory": str(args.output_dir),
        "file_format": "netcdf",
        "netcdf_compression_level": 4,
        "overwrite": False,
    }

    if args.dry_run:
        print("Dry run: no network request made.")
        return

    copernicusmarine.subset(**request)
    if not nc_path.exists():
        raise FileNotFoundError(f"Copernicus subset did not create {nc_path}")

    ds = xr.open_dataset(nc_path)
    try:
        print(f"  dimensions: {dict(ds.sizes)}")
        print(f"  variables : {[v for v in VARIABLES if v in ds.data_vars]}")
    finally:
        ds.close()

    table = normalize(nc_path)
    table.to_parquet(parquet_path, index=False)
    print(f"Transformed: {parquet_path}")
    print(f"Rows: {len(table)}")


if __name__ == "__main__":
    main()
