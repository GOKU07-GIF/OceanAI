"""Validate normalized OceanAI observation files.

Checks schema, coordinates, timestamps, and broad physical plausibility ranges.
The ranges are intentionally conservative quality gates; they do not decide
whether an observation is safe for fishing or navigation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
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
}

RANGES: dict[str, tuple[float, float]] = {
    "sst_c": (-5.0, 45.0),
    "temperature_c": (-5.0, 45.0),
    "salinity_psu": (0.0, 45.0),
    "wave_height_m": (0.0, 30.0),
    "wave_period_s": (0.0, 60.0),
    "wave_direction_deg": (0.0, 360.0),
    "chlorophyll_mg_m3": (0.0, 100.0),
    "current_speed_ms": (0.0, 10.0),
    "current_direction_deg": (0.0, 360.0),
    "wind_speed_m_s": (0.0, 80.0),
    "wind_stress_pa": (0.0, 10.0),
    "mld_m": (0.0, 6000.0),
    "d20_m": (0.0, 6000.0),
}


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported file format: {path}")


def validate(path: Path) -> tuple[int, list[str]]:
    frame = read_table(path)
    errors: list[str] = []

    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        errors.append(f"missing columns: {sorted(missing)}")
        return len(frame), errors

    timestamps = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    if timestamps.isna().any():
        errors.append(f"invalid timestamps: {int(timestamps.isna().sum())}")

    for column, low, high in (
        ("latitude", -90.0, 90.0),
        ("longitude", -180.0, 180.0),
    ):
        values = pd.to_numeric(frame[column], errors="coerce")
        bad = values.isna() | (values < low) | (values > high)
        if bad.any():
            errors.append(f"invalid {column}: {int(bad.sum())}")

    values = pd.to_numeric(frame["value"], errors="coerce")
    if values.isna().any():
        errors.append(f"invalid value cells: {int(values.isna().sum())}")

    for variable, (low, high) in RANGES.items():
        mask = frame["variable"].astype(str).str.strip().str.lower() == variable
        if not mask.any():
            continue
        numeric = pd.to_numeric(frame.loc[mask, "value"], errors="coerce")
        bad = numeric.isna() | (numeric < low) | (numeric > high)
        if bad.any():
            errors.append(
                f"{variable} outside broad range [{low}, {high}]: {int(bad.sum())}"
            )

    return len(frame), errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate normalized OceanAI observation files")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    total_rows = 0
    failures = 0
    for path in args.files:
        if not path.exists():
            print(f"FAIL {path}: file not found")
            failures += 1
            continue
        rows, errors = validate(path)
        total_rows += rows
        if errors:
            failures += 1
            print(f"FAIL {path}: {len(errors)} issue(s)")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}: {rows} rows")

    print(f"Total rows checked: {total_rows}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
