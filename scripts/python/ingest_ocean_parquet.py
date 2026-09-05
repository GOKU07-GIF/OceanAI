"""Ingest normalized OceanAI Parquet/CSV files into PostgreSQL.

The input files are expected to use the canonical ocean observation schema:
    timestamp, latitude, longitude, depth_m, variable, value, unit,
    source, dataset, data_type, quality_flag

Provider-specific variable names are mapped to canonical names before insert
so the shared observation store can be queried consistently by ORCA.

The database URL is taken from DATABASE_URL when explicitly set. Otherwise,
the existing OceanAI application settings are used, which load backend/.env.
The script is deliberately separate from the download pipeline so acquisition
and database loading can be retried independently.

Examples:
  python scripts/python/ingest_ocean_parquet.py datasets/raw/incois/sst_*.parquet
  python scripts/python/ingest_ocean_parquet.py datasets/raw/incois/*.csv --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# scripts/python/ -> scripts/ -> repository root; backend/ contains the `app`
# package used by the SQLAlchemy model. Add it explicitly so this CLI works
# without requiring PYTHONPATH to be configured by the caller.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ocean_observation import OceanObservation

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

DEFAULT_CHUNK_SIZE = 5000

# Provider -> canonical OceanAI variable names.
VARIABLE_ALIASES = {
    "sst": "sst_c",
    "anom": "sst_anomaly_c",
    "MLD": "mld_m",
    "D20": "d20_m",
    "GEO_U": "current_u_cm_s",
    "GEO_V": "current_v_cm_s",
    "WIND_SPEED": "wind_speed_m_s",
    "CHL": "chlorophyll_mg_m3",
    "SAL": "salinity_psu",
    "TEMP": "temperature_c",
}

UNIT_ALIASES = {
    "sst_c": "degC",
    "sst_anomaly_c": "degC",
    "mld_m": "m",
    "d20_m": "m",
    "current_u_cm_s": "cm/s",
    "current_v_cm_s": "cm/s",
    "wind_speed_m_s": "m/s",
    "chlorophyll_mg_m3": "mg/m3",
    "salinity_psu": "PSU",
    "temperature_c": "degC",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest normalized ocean files into PostgreSQL")
    parser.add_argument("files", nargs="+", type=Path, help="CSV or Parquet input files")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--dry-run", action="store_true", help="Validate and report rows without inserting")
    return parser.parse_args()


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        frame = pd.read_parquet(path)
    elif path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported input format: {path}")

    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"{path}: missing columns: {sorted(missing)}")

    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    for column in ["latitude", "longitude", "depth_m", "value"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    if frame["timestamp"].isna().any():
        raise ValueError(f"{path}: invalid timestamp values found")
    if frame[["latitude", "longitude", "value"]].isna().any().any():
        raise ValueError(f"{path}: invalid numeric coordinate/value found")

    frame["quality_flag"] = frame["quality_flag"].fillna("present").astype(str)
    frame["source"] = frame["source"].astype(str)
    frame["dataset"] = frame["dataset"].astype(str)
    frame["data_type"] = frame["data_type"].astype(str)

    raw_variables = frame["variable"].astype(str)
    frame["variable"] = raw_variables.map(lambda name: VARIABLE_ALIASES.get(name, name))
    frame["unit"] = frame["unit"].fillna("").astype(str)
    frame["unit"] = frame.apply(
        lambda row: UNIT_ALIASES.get(row["variable"], row["unit"]),
        axis=1,
    )

    return frame[
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
    ]


def insert_frame(session: Session, frame: pd.DataFrame, chunk_size: int) -> int:
    records = frame.where(pd.notna(frame), None).to_dict(orient="records")
    inserted = 0

    for start in range(0, len(records), chunk_size):
        chunk = records[start : start + chunk_size]
        statement = insert(OceanObservation).values(chunk)
        statement = statement.on_conflict_do_nothing(
            constraint="uq_ocean_observation_identity"
        )
        result = session.execute(statement)
        inserted += result.rowcount or 0

    return inserted


def main() -> None:
    args = parse_args()
    files = [path for path in args.files if path.exists()]
    if not files:
        raise SystemExit("No input files found")

    total_rows = 0
    total_inserted = 0

    engine = None
    session = None
    if not args.dry_run:
        database_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
        if not database_url:
            raise SystemExit(
                "Database URL is unavailable. Set DATABASE_URL or configure it in backend/.env"
            )
        engine = create_engine(database_url, pool_pre_ping=True)
        session = Session(engine)

    try:
        for path in files:
            frame = read_table(path)
            total_rows += len(frame)
            print(f"{path}: {len(frame)} normalized rows")

            if session is not None:
                inserted = insert_frame(session, frame, args.chunk_size)
                total_inserted += inserted
                session.commit()
                print(f"  inserted: {inserted}")

        print(f"Total rows validated: {total_rows}")
        if args.dry_run:
            print("Dry run: no rows inserted")
        else:
            print(f"Total rows inserted: {total_inserted}")
    except Exception:
        if session is not None:
            session.rollback()
        raise
    finally:
        if session is not None:
            session.close()
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    main()
