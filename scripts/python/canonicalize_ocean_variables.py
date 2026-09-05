"""Convert provider-native ocean variable names to OceanAI canonical names.

The normalized data layer keeps one vocabulary so ORCA can reason over data
from INCOIS, Copernicus, NOAA, and other providers without provider-specific
checks in every caller.

Usage from repository root:
  python scripts/python/canonicalize_ocean_variables.py \
      --input datasets/raw/incois/value_added_....parquet \
      --output datasets/processed/incois/value_added_....parquet
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

VARIABLE_MAP = {
    # INCOIS SST
    "sst": "sst_c",
    "anom": "sst_anomaly_c",
    # INCOIS value-added products
    "MLD": "mld_m",
    "ILD": "ild_m",
    "D26": "d26_m",
    "D20": "d20_m",
    "GEO_U": "current_u_cm_s",
    "GEO_V": "current_v_cm_s",
    # INCOIS Oceansat-2 OCM
    "CHL": "chlorophyll_mg_m3",
    # Common Copernicus aliases
    "thetao": "temperature_c",
    "so": "salinity_psu",
    "uo": "current_u_ms",
    "vo": "current_v_ms",
    "zos": "sea_level_m",
    "VHM0": "wave_height_m",
    "VTM02": "wave_period_s",
    "VMDR": "wave_direction_deg",
    "chl": "chlorophyll_mg_m3",
    # INCOIS wind product
    "WIND_SPEED": "wind_speed_m_s",
}

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonicalize OceanAI variable names")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise SystemExit("Input must be .parquet or .csv")


def main() -> None:
    args = parse_args()
    frame = read_table(args.input)

    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {sorted(missing)}")

    frame = frame.copy()
    frame["variable"] = frame["variable"].map(VARIABLE_MAP).fillna(frame["variable"])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".parquet":
        frame.to_parquet(args.output, index=False)
    elif args.output.suffix.lower() == ".csv":
        frame.to_csv(args.output, index=False)
    else:
        raise SystemExit("Output must be .parquet or .csv")

    print(f"Canonicalized {len(frame)} rows -> {args.output}")
    print("Variables:")
    for variable in sorted(frame["variable"].dropna().unique()):
        print(f"  - {variable}")


if __name__ == "__main__":
    main()
