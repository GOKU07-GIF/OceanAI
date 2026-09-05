from __future__ import annotations

from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from typing import Any, Iterable

from sqlalchemy.orm import Session

from app.models.ocean_data import OceanData
from app.models.ocean_observation import OceanObservation


_VARIABLE_ALIASES: dict[str, str] = {
    "sst": "sst_c",
    "sst_c": "sst_c",
    "analysed_sst": "sst_c",
    "temperature": "temperature_c",
    "thetao": "temperature_c",
    "wave_height": "wave_height_m",
    "wave_height_m": "wave_height_m",
    "vhm0": "wave_height_m",
    "wave_period": "wave_period_s",
    "wave_period_s": "wave_period_s",
    "vtm02": "wave_period_s",
    "wave_direction": "wave_direction_deg",
    "wave_direction_deg": "wave_direction_deg",
    "vmdr": "wave_direction_deg",
    "chl": "chlorophyll_mg_m3",
    "chlorophyll": "chlorophyll_mg_m3",
    "chlorophyll_mg_m3": "chlorophyll_mg_m3",
    "sal": "salinity_psu",
    "salinity": "salinity_psu",
    "salinity_psu": "salinity_psu",
    "so": "salinity_psu",
    "mld": "mld_m",
    "mld_m": "mld_m",
    "d20": "d20_m",
    "d20_m": "d20_m",
    "geo_u": "current_u_cm_s",
    "geo_v": "current_v_cm_s",
    "current_u_cm_s": "current_u_cm_s",
    "current_v_cm_s": "current_v_cm_s",
    "uo": "current_u_m_s",
    "vo": "current_v_m_s",
    "wind_speed": "wind_speed_m_s",
    "wind_speed_m_s": "wind_speed_m_s",
    "wind_stress": "wind_stress_pa",
}

_REQUEST_TO_VARIABLES: dict[str, set[str]] = {
    "sst_c": {"sst_c"},
    "wave_height_m": {"wave_height_m"},
    "wave_period_s": {"wave_period_s"},
    "wave_direction_deg": {"wave_direction_deg"},
    "chlorophyll_mg_m3": {"chlorophyll_mg_m3"},
    "salinity_psu": {"salinity_psu"},
    "temperature_c": {"temperature_c", "sst_c"},
}


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


def _canonical_variable(variable: str) -> str:
    normalized = variable.strip().lower()
    return _VARIABLE_ALIASES.get(normalized, normalized)


def _requested_canonical_variables(requested_variables: Iterable[str] | None) -> set[str] | None:
    if requested_variables is None:
        return None

    result: set[str] = set()
    for item in requested_variables:
        canonical = _canonical_variable(item)
        result.update(_REQUEST_TO_VARIABLES.get(canonical, {canonical}))
    return result


def _serialize_observation(row: OceanObservation, distance_km: float) -> dict[str, Any]:
    timestamp = row.timestamp.isoformat() if isinstance(row.timestamp, datetime) else str(row.timestamp)
    return {
        "latitude": row.latitude,
        "longitude": row.longitude,
        "depth_m": row.depth_m,
        "distance_km": round(distance_km, 2),
        "timestamp": timestamp,
        "variable": _canonical_variable(row.variable),
        "raw_variable": row.variable,
        "value": row.value,
        "unit": row.unit,
        "source": row.source,
        "dataset": row.dataset,
        "data_type": row.data_type,
        "quality_flag": row.quality_flag,
    }


def _query_normalized_observations(
    *,
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float,
    limit: int,
    requested_variables: set[str] | None,
    start_time: str | None,
    end_time: str | None,
) -> list[dict[str, Any]]:
    """Query the shared normalized data store around a selected point."""
    lat_delta = radius_km / 111.0
    lon_scale = max(cos(radians(latitude)), 0.2)
    lon_delta = radius_km / (111.0 * lon_scale)

    query = db.query(OceanObservation).filter(
        OceanObservation.latitude.between(latitude - lat_delta, latitude + lat_delta),
        OceanObservation.longitude.between(longitude - lon_delta, longitude + lon_delta),
    )

    if start_time:
        query = query.filter(OceanObservation.timestamp >= start_time)
    if end_time:
        query = query.filter(OceanObservation.timestamp <= end_time)

    rows = query.order_by(OceanObservation.timestamp.desc()).limit(max(limit * 100, 500)).all()

    observations: list[dict[str, Any]] = []
    for row in rows:
        canonical = _canonical_variable(row.variable)
        if requested_variables and canonical not in requested_variables:
            continue

        distance = _distance_km(latitude, longitude, row.latitude, row.longitude)
        if distance > radius_km:
            continue

        observations.append(_serialize_observation(row, distance))

    observations.sort(key=lambda item: (item["distance_km"], item["timestamp"]))

    selected: list[dict[str, Any]] = []
    seen_variables: set[str] = set()
    for item in observations:
        key = item["variable"]
        if key in seen_variables:
            continue
        seen_variables.add(key)
        selected.append(item)
        if len(selected) >= limit:
            break

    return selected


def _query_legacy_observations(
    *,
    db: Session,
    latitude: float,
    longitude: float,
    owner_id: int,
    radius_km: float,
    limit: int,
) -> list[dict[str, Any]]:
    """Compatibility fallback for the original user-owned OceanData table."""
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
        timestamp = created_at.isoformat() if isinstance(created_at, datetime) else str(created_at)
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
                "variable": "legacy_ocean_data",
                "source": "OceanAI PostgreSQL",
                "dataset": "OceanData",
                "data_type": "legacy_local_observation",
                "quality_flag": "present",
            }
        )

    observations.sort(key=lambda item: (item["distance_km"], item["timestamp"]))
    return observations[:limit]


def get_ocean_conditions(
    *,
    db: Session,
    latitude: float,
    longitude: float,
    owner_id: int,
    radius_km: float = 250.0,
    limit: int = 20,
    requested_variables: Iterable[str] | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict[str, Any]:
    """Return nearby normalized ocean data for ORCA with source provenance.

    Normalized provider data is shared reference data and is queried from
    ``ocean_observations`` without the legacy owner filter. The old OceanData
    table remains a fallback so existing deployments do not break before the
    first real provider-data ingestion completes.
    """
    requested = _requested_canonical_variables(requested_variables)
    observations = _query_normalized_observations(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
        requested_variables=requested,
        start_time=start_time,
        end_time=end_time,
    )

    if observations:
        return {
            "status": "success",
            "source": "OceanAI normalized observation store",
            "dataset": "ocean_observations",
            "type": "normalized_ocean_observation",
            "location": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "requested_variables": sorted(requested) if requested else [],
            "observations": observations,
            "observation_count": len(observations),
        }

    legacy = _query_legacy_observations(
        db=db,
        latitude=latitude,
        longitude=longitude,
        owner_id=owner_id,
        radius_km=radius_km,
        limit=limit,
    )
    return {
        "status": "success",
        "source": "OceanAI PostgreSQL",
        "dataset": "OceanData",
        "type": "legacy_local_observation",
        "location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "requested_variables": sorted(requested) if requested else [],
        "observations": legacy,
        "observation_count": len(legacy),
        "fallback": True,
    }
