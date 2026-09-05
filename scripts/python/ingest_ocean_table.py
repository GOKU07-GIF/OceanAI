"""Load normalized OceanAI CSV/Parquet data into PostgreSQL.

The input schema is:
  timestamp, latitude, longitude, variable, value, unit,
  source, dataset, data_type, quality_flag

Usage:
  python scripts/python/ingest_ocean_table.py --file datasets/raw/incois/example.parquet

The database URL is read from DATABASE_URL unless --database-url is supplied.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

REQUIRED_COLUMNS = [
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

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ocean_observations (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    variable VARCHAR(64) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(32),
    source VARCHAR(64) NOT NULL,
    dataset VARCHAR(160) NOT NULL,
    data_type VARCHAR(32) NOT NULL,
    quality_flag VARCHAR(32) NOT NULL DEFAULT 'present',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (timestamp, latitude, longitude, variable, source, dataset)
);
"""

INSERT_SQL = """
INSERT INTO ocean_observations
    (timestamp, latitude, longitude, variable, value, unit, source, dataset, data_type, quality_flag)
VALUES %s
ON CONFLICT (timestamp, latitude, longitude, variable, source, dataset)
DO UPDATE SET
    value = EXCLUDED.value,
    unit = EXCLUDED.unit,
    data_type = EXCLUDED.data_type,
    quality_flag = EXCLUDED.quality_flag;
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest normalized OceanAI observations")
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--chunk-size", type=int, default=5000)
    return parser.parse_args()


def load_frame(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    elif path.suffix.lower() == ".parquet":
        frame = pd.read_parquet(path)
    else:
        raise ValueError("Input file must be CSV or Parquet")

    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = frame[REQUIRED_COLUMNS].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="raise")
    frame["latitude"] = pd.to_numeric(frame["latitude"], errors="raise")
    frame["longitude"] = pd.to_numeric(frame["longitude"], errors="raise")
    frame["value"] = pd.to_numeric(frame["value"], errors="raise")

    if frame.empty:
        raise ValueError("Input contains no rows")
    if not frame[["latitude", "longitude"]].apply(lambda column: column.notna().all()).all():
        raise ValueError("Latitude/longitude contains nulls")

    return frame


def main() -> None:
    args = parse_args()
    if not args.database_url:
        raise SystemExit("DATABASE_URL is required")

    frame = load_frame(args.file)

    with psycopg2.connect(args.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TABLE_SQL)
            rows = [
                (
                    row.timestamp.to_pydatetime(),
                    float(row.latitude),
                    float(row.longitude),
                    str(row.variable),
                    float(row.value),
                    str(row.unit) if pd.notna(row.unit) else None,
                    str(row.source),
                    str(row.dataset),
                    str(row.data_type),
                    str(row.quality_flag),
                )
                for row in frame.itertuples(index=False)
            ]

            for start in range(0, len(rows), args.chunk_size):
                execute_values(cursor, INSERT_SQL, rows[start : start + args.chunk_size])

    print(f"Ingested {len(frame)} observations from {args.file}")


if __name__ == "__main__":
    main()
