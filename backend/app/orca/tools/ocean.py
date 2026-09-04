from __future__ import annotations

from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from typing import Any

from sqlalchemy.orm import Session

from app.models.ocean_data import OceanData


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance between two coordinates in kilometres."""
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))


def get_ocean_conditions(
    *,
    db: Session,
    latitude: float,
    longitude: float,
    owner_id: int,
    radius_km: float = 250.0,
    limit: int = 10,
) -> dict[str, Any]:
    """Fetch nearby OceanAI observations for the authenticated user.

    This adapter deliberately uses OceanAI's PostgreSQL data first. It is an
    internal source adapter, not a claim that these observations originate
    from INCOIS/ISRO/Copernicus. External authoritative adapters can be added
    later without changing the ORCA agent contract.
    """
    rows = (
        db.query(OceanData)
        .filter(
            OceanData.owner_id == owner_id,
            OceanData.is_active.is_(True),
        )
        .order_by(OceanData.created_at.desc())
        .limit(200)
        .all()
    )

    observations: list[dict[str, Any]] = []
    for row in rows:
        distance = _distance_km(latitude, longitude, row.latitude, row.longitude)
        if distance > radius_km:
            continue

        created_at = row.created_at
        if isinstance(created_at, datetime):
            timestamp = created_at.isoformat()
        else:
            timestamp = str(created_at)

        observations.append(
            {
                "latitude": row.latitude,
                "longitude": row.longitude,
                "distance_km": round(distance, 2),
                "temperature_c": row.temperature,
                "ph": row.ph,
                "salinity": row.salinity,
                "oxygen": row.oxygen,
                "is_active": row.is_active,
                "timestamp": timestamp,
            }
        )

    observations.sort(key=lambda item: (item["distance_km"], item["timestamp"]), reverse=False)
    observations = observations[:limit]

    return {
        "status": "success",
        "source": "OceanAI PostgreSQL",
        "dataset": "OceanData",
        "type": "local_observation",
        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "radius_km": radius_km,
        "observations": observations,
        "observation_count": len(observations),
    }
