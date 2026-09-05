"""Report the state of the normalized OceanAI observation store.

The report is intentionally read-only. It helps us verify that real provider
data has been ingested before ORCA is allowed to rely on the shared store.

Usage from repository root or backend directory:
  python scripts/python/report_ocean_data.py
  python scripts/python/report_ocean_data.py --variable sst_c
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

# Make the backend package importable when this script is invoked directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Load the project's backend/.env when DATABASE_URL is not already exported.
try:
    from dotenv import load_dotenv
except ImportError as exc:  # pragma: no cover - dependency/configuration boundary
    raise SystemExit(
        "python-dotenv is required. Run: python -m pip install python-dotenv"
    ) from exc

load_dotenv(BACKEND_ROOT / ".env", override=False)

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from app.models.ocean_observation import OceanObservation


CANONICAL_VARIABLES = (
    "sst_c",
    "wave_height_m",
    "wave_period_s",
    "wave_direction_deg",
    "wind_speed_m_s",
    "chlorophyll_mg_m3",
    "salinity_psu",
    "mld_m",
    "d20_m",
    "current_u_cm_s",
    "current_v_cm_s",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report OceanAI normalized data readiness")
    parser.add_argument("--variable", choices=CANONICAL_VARIABLES)
    parser.add_argument("--source")
    return parser.parse_args()


def build_query(session: Session, variable: str | None, source: str | None) -> Sequence[tuple]:
    query = session.query(
        OceanObservation.variable,
        func.count(OceanObservation.id).label("rows"),
        func.min(OceanObservation.timestamp).label("first_timestamp"),
        func.max(OceanObservation.timestamp).label("last_timestamp"),
    )

    if variable:
        query = query.filter(OceanObservation.variable == variable)
    if source:
        query = query.filter(OceanObservation.source == source)

    return query.group_by(OceanObservation.variable).order_by(OceanObservation.variable).all()


def main() -> None:
    args = parse_args()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            f"DATABASE_URL not found. Export it or add it to {BACKEND_ROOT / '.env'}"
        )

    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with Session(engine) as session:
            total = session.query(func.count(OceanObservation.id)).scalar() or 0
            sources = (
                session.query(OceanObservation.source)
                .distinct()
                .order_by(OceanObservation.source)
                .all()
            )
            print(f"Normalized observation rows: {total}")
            print("Sources:")
            for (source,) in sources:
                print(f"  - {source}")

            rows = build_query(session, args.variable, args.source)
            if not rows:
                print("No matching observations.")
                return

            print("\nVariable readiness:")
            for variable, count, first_timestamp, last_timestamp in rows:
                print(
                    f"  {variable}: rows={count}, "
                    f"first={first_timestamp}, last={last_timestamp}"
                )

            missing = [
                variable
                for variable in CANONICAL_VARIABLES
                if not session.query(OceanObservation.id)
                .filter(OceanObservation.variable == variable)
                .first()
            ]
            print("\nCanonical variables without data:")
            if missing:
                for variable in missing:
                    print(f"  - {variable}")
            else:
                print("  none")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
