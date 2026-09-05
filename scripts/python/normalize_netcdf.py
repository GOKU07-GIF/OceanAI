"""Normalize an INCOIS/ROMS NetCDF file into OceanAI's canonical table.

This utility is intentionally provider-agnostic. It can ingest a downloaded
NetCDF file once the official provider exposes it, without hard-coding an
unverified ROMS download URL.

Canonical columns:
  timestamp, latitude, longitude, variable, value, unit, source, dataset,
  data_type, quality_flag

Examples:
  python scripts/python/normalize_netcdf.py --input datasets/raw/incois/file.nc --output datasets/processed/file.parquet --source INCOIS --dataset incois_roms --data-type forecast
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import xarray as xr

COORD_ALIASES = {
    "time": ["time", "datetime", "date"],
    "latitude": ["latitude", "lat", "nav_lat"],
    "longitude": ["longitude", "lon", "nav_lon"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize a gridded NetCDF file")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--data-type", default="observation")
    return parser.parse_args()


def find_coord(ds: xr.Dataset, aliases: list[str]) -> str | None:
    names = set(ds.coords) | set(ds.dims)
    lower = {name.lower(): name for name in names}
    for alias in aliases:
        if alias in lower:
            return lower[alias]
    for name in names:
        normalized = name.lower().replace("_", "")
        if any(alias.replace("_", "") in normalized for alias in aliases):
            return name
    return None


def normalize(input_path: Path, source: str, dataset: str, data_type: str) -> pd.DataFrame:
    ds = xr.open_dataset(input_path)
    try:
        time_name = find_coord(ds, COORD_ALIASES["time"])
        lat_name = find_coord(ds, COORD_ALIASES["latitude"])
        lon_name = find_coord(ds, COORD_ALIASES["longitude"])

        missing = [name for name, value in (("time", time_name), ("latitude", lat_name), ("longitude", lon_name)) if value is None]
        if missing:
            raise ValueError(f"Could not identify required coordinates: {missing}")

        frame = ds.to_dataframe().reset_index()
        coordinate_names = {time_name, lat_name, lon_name}
        # Keep non-coordinate data variables as individual long-form observations.
        value_columns = [column for column in frame.columns if column not in coordinate_names]
        if not value_columns:
            raise ValueError("No data variables found in NetCDF")

        rows: list[pd.DataFrame] = []
        for variable in value_columns:
            part = frame[[time_name, lat_name, lon_name, variable]].copy()
            part = part.rename(columns={time_name: "timestamp", lat_name: "latitude", lon_name: "longitude", variable: "value"})
            part["variable"] = variable
            part["source"] = source
            part["dataset"] = dataset
            part["data_type"] = data_type
            part["quality_flag"] = "present"
            part = part.dropna(subset=["value"])
            if not part.empty:
                rows.append(part)

        if not rows:
            raise ValueError("No non-null observations found")

        result = pd.concat(rows, ignore_index=True)
        result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True, errors="coerce")
        if result["timestamp"].isna().any():
            raise ValueError("One or more timestamps could not be normalized")
        result["unit"] = ""

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
    finally:
        ds.close()


def main() -> None:
    args = parse_args()
    table = normalize(args.input, args.source, args.dataset, args.data_type)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".csv":
        table.to_csv(args.output, index=False)
    elif args.output.suffix.lower() == ".parquet":
        table.to_parquet(args.output, index=False)
    else:
        raise SystemExit("Output must end with .csv or .parquet")
    print(f"Normalized {len(table)} observations -> {args.output}")


if __name__ == "__main__":
    main()
