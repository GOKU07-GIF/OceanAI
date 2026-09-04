"""Basic validation for OceanAI NetCDF downloads.

Usage:
  python scripts/python/validate_netcdf.py datasets/raw/copernicus/<file>.nc

This checks structure and basic coordinate/value sanity. It does not decide
whether a dataset is scientifically fit for every ORCA use case.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import xarray as xr


REQUIRED_COORD_NAMES = {
    "lat": {"lat", "latitude"},
    "lon": {"lon", "longitude"},
}


def find_coord(ds: xr.Dataset, candidates: set[str]) -> str | None:
    for name in candidates:
        if name in ds.coords or name in ds.variables:
            return name
    return None


def validate(path: Path) -> int:
    if not path.exists():
        print(f"FAIL: file does not exist: {path}")
        return 1
    if path.suffix.lower() not in {".nc", ".nc4", ".netcdf"}:
        print(f"FAIL: expected a NetCDF file, got: {path.name}")
        return 1

    print(f"Opening: {path}")
    try:
        ds = xr.open_dataset(path)
    except Exception as exc:  # noqa: BLE001 - CLI should show the provider/parser error
        print(f"FAIL: could not open NetCDF: {exc}")
        return 1

    failures: list[str] = []
    try:
        print(f"Dimensions: {dict(ds.sizes)}")
        print(f"Variables: {', '.join(ds.data_vars)}")

        lat_name = find_coord(ds, REQUIRED_COORD_NAMES["lat"])
        lon_name = find_coord(ds, REQUIRED_COORD_NAMES["lon"])
        if lat_name is None:
            failures.append("latitude coordinate not found")
        if lon_name is None:
            failures.append("longitude coordinate not found")

        for name, label in ((lat_name, "latitude"), (lon_name, "longitude")):
            if name is None:
                continue
            values = np.asarray(ds[name].values, dtype=float)
            finite = values[np.isfinite(values)]
            if finite.size == 0:
                failures.append(f"{label} contains no finite values")
                continue
            print(f"{label}: min={finite.min():.6g}, max={finite.max():.6g}")
            if label == "latitude" and (finite.min() < -90 or finite.max() > 90):
                failures.append("latitude is outside [-90, 90]")
            if label == "longitude" and (finite.min() < -360 or finite.max() > 360):
                failures.append("longitude is outside a valid global range")

        time_names = [name for name in ("time", "datetime", "date") if name in ds.coords or name in ds.variables]
        if not time_names:
            failures.append("time coordinate not found")
        else:
            time_name = time_names[0]
            values = ds[time_name].values
            if len(values) == 0:
                failures.append("time coordinate is empty")
            else:
                print(f"time: first={values[0]}, last={values[-1]}, count={len(values)}")

        for variable in ds.data_vars:
            values = np.asarray(ds[variable].values)
            if values.size == 0:
                failures.append(f"variable '{variable}' is empty")
                continue
            finite_count = np.isfinite(values).sum() if np.issubdtype(values.dtype, np.number) else values.size
            if finite_count == 0:
                failures.append(f"variable '{variable}' contains no finite numeric values")
            print(f"  {variable}: shape={values.shape}, finite={finite_count}/{values.size}")
    finally:
        ds.close()

    if failures:
        print("\nVALIDATION: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nVALIDATION: PASS")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an OceanAI NetCDF dataset")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    raise SystemExit(validate(args.file))


if __name__ == "__main__":
    main()
