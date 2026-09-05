"""Build a machine-readable manifest for acquired normalized ocean data.

The manifest is deliberately generated from local files. A dataset is only
reported as acquired when a real NetCDF/CSV/Parquet file exists and passes the
basic schema/time checks performed here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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

SUPPORTED_SUFFIXES = {".csv", ".parquet"}


def inspect_table(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".parquet":
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path)

    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        return {"status": "invalid", "file": str(path), "missing_columns": missing}

    timestamps = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    if timestamps.isna().any():
        return {"status": "invalid", "file": str(path), "error": "invalid timestamps"}

    numeric = frame[["latitude", "longitude", "value"]].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any():
        return {"status": "invalid", "file": str(path), "error": "invalid numeric values"}

    return {
        "status": "validated",
        "file": str(path),
        "rows": int(len(frame)),
        "variables": sorted(frame["variable"].astype(str).unique().tolist()),
        "sources": sorted(frame["source"].astype(str).unique().tolist()),
        "datasets": sorted(frame["dataset"].astype(str).unique().tolist()),
        "min_timestamp": timestamps.min().isoformat(),
        "max_timestamp": timestamps.max().isoformat(),
        "non_null_values": int(frame["value"].notna().sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an OceanAI data manifest")
    parser.add_argument("directory", type=Path, help="Directory containing normalized CSV/Parquet files")
    parser.add_argument("--output", type=Path, default=Path("datasets/manifest.json"))
    args = parser.parse_args()

    files = sorted(p for p in args.directory.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES)
    records = [inspect_table(path) for path in files]

    validated = [record for record in records if record["status"] == "validated"]
    manifest = {
        "version": 1,
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "directory": str(args.directory),
        "file_count": len(records),
        "validated_file_count": len(validated),
        "total_rows": sum(record.get("rows", 0) for record in validated),
        "records": records,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps(manifest, indent=2))
    if records and len(validated) != len(records):
        raise SystemExit("One or more normalized data files failed validation")


if __name__ == "__main__":
    main()
