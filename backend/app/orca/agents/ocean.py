from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.orca.marine.local_cache import get_cached_copernicus_sst
from app.orca.marine.models import MarineDataRequest
from app.orca.marine.provider import marine_provider
from app.orca.state import ORCAState
from app.orca.tools.ocean import get_ocean_conditions
from app.orca.tools.registry import tool_registry


_MARINE_SAFETY_VARIABLES = [
    "sst_c",
    "salinity_psu",
    "wave_height_m",
    "wave_period_s",
]

_MARINE_FISHING_VARIABLES = [
    "sst_c",
    "salinity_psu",
    "wave_height_m",
    "wave_period_s",
    "chlorophyll_mg_m3",
]

# Keep user-facing ORCA requests fast. Waves remain live/operational data;
# slower physics and ocean-colour values are read from the normalized store
# when a recent cached observation exists. A missing/stale cache must never
# block a safety response.
_LIVE_MARINE_VARIABLES = [
    "wave_height_m",
    "wave_period_s",
]

_CACHED_MARINE_VARIABLES = [
    "sst_c",
    "salinity_psu",
    "chlorophyll_mg_m3",
]

_MARINE_CACHE_MAX_AGE_DAYS = 14
_LOCAL_SST_MAX_DISTANCE_KM = 75.0
_LOCAL_SST_MAX_DEPTH_M = 10.0

_FISHING_TERMS = ("fishing", "fish", "pfz", "fishing zone")


def _build_cached_conditions(
    result: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Convert recent normalized observations into ORCA condition fields."""
    if result.get("fallback"):
        # Do not use the legacy user-owned OceanData table as a marine cache.
        return {}, []

    conditions: dict[str, Any] = {}
    observations = result.get("observations", [])
    contributions: list[dict[str, Any]] = []

    if not isinstance(observations, list):
        return conditions, contributions

    for observation in observations:
        if not isinstance(observation, dict):
            continue

        variable = observation.get("variable")
        value = observation.get("value")
        if variable not in _CACHED_MARINE_VARIABLES:
            continue
        if not isinstance(value, (int, float)):
            continue

        conditions[variable] = float(value)
        contributions.append(
            {
                "provider": "OceanAI normalized observation store",
                "source": str(
                    observation.get(
                        "source",
                        "OceanAI normalized observation store",
                    )
                ),
                "dataset": str(
                    observation.get(
                        "dataset",
                        "ocean_observations",
                    )
                ),
                "type": "recent_cached_observation",
                "variables": [variable],
                "timestamp": observation.get("timestamp"),
                "distance_km": observation.get("distance_km"),
            }
        )

    return conditions, contributions


def run_ocean_agent(state: ORCAState) -> dict[str, Any]:
    """Collect normalized observations plus fast authoritative marine context."""
    location = state.get("location")
    db = state.get("db")
    if not location:
        return {
            "agent_results": [
                {
                    "agent": "ocean",
                    "status": "error",
                    "error": "Location is required for ocean intelligence.",
                }
            ],
            "errors": ["Ocean agent could not run because location is missing."],
        }

    if not isinstance(db, Session):
        return {
            "agent_results": [
                {
                    "agent": "ocean",
                    "status": "error",
                    "error": "Database session is unavailable for OceanAI observations.",
                }
            ],
            "errors": ["Ocean agent could not access the OceanAI database."],
        }

    query = state.get("query", "").lower()
    is_fishing_query = any(term in query for term in _FISHING_TERMS)
    requested_variables = (
        _MARINE_FISHING_VARIABLES
        if is_fishing_query
        else _MARINE_SAFETY_VARIABLES
    )

    updates: dict[str, Any] = {
        "agent_results": [],
        "evidence": [],
        "errors": [],
    }

    requested_time = state.get("requested_time") or {}

    # Keep the historical/normalized observation context visible, but never
    # require it for the live safety path.
    local_result = get_ocean_conditions(
        db=db,
        latitude=location["latitude"],
        longitude=location["longitude"],
        owner_id=state["user_id"],
        radius_km=250.0,
        limit=20,
        requested_variables=requested_variables,
        start_time=requested_time.get("start"),
        end_time=requested_time.get("end"),
    )

    local_agent_result = {
        "agent": "ocean",
        "status": local_result.get("status", "error"),
        "source": local_result.get(
            "source",
            "OceanAI normalized observation store",
        ),
        "dataset": local_result.get(
            "dataset",
            "ocean_observations",
        ),
        "observation_count": local_result.get(
            "observation_count",
            0,
        ),
        "observations": local_result.get(
            "observations",
            [],
        ),
        "fallback": local_result.get(
            "fallback",
            False,
        ),
    }

    updates["agent_results"].append(local_agent_result)

    if local_result.get("status") == "success" and not local_result.get("fallback"):
        updates["evidence"].append(local_result)

    # ------------------------------------------------------------------
    # Live marine path: only fetch the fast operational wave dataset here.
    # SST, salinity, and chlorophyll come from a recent normalized cache when
    # available. This prevents a user request from waiting on slow remote
    # physics/ocean-colour dataset opens.
    # ------------------------------------------------------------------
    marine_request: MarineDataRequest = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "variables": list(_LIVE_MARINE_VARIABLES),
        "radius_km": 50.0,
    }

    if requested_time.get("start"):
        marine_request["start_time"] = requested_time["start"]

    if requested_time.get("end"):
        marine_request["end_time"] = requested_time["end"]

    marine_result = marine_provider.fetch(
        request=marine_request,
        provider_order=("copernicus",),
    )

    marine_data = marine_result.get("data")

    # Recent cache lookup deliberately ignores the requested future window:
    # it is context data, not a forecast. Only observations newer than the
    # cache horizon are eligible, and legacy fallback data is rejected.
    cache_cutoff = (
        datetime.now(timezone.utc)
        - timedelta(days=_MARINE_CACHE_MAX_AGE_DAYS)
    ).isoformat()
    cache_result = get_ocean_conditions(
        db=db,
        latitude=location["latitude"],
        longitude=location["longitude"],
        owner_id=state["user_id"],
        radius_km=50.0,
        limit=20,
        requested_variables=_CACHED_MARINE_VARIABLES,
        start_time=cache_cutoff,
        end_time=None,
    )
    cached_conditions, cached_contributions = _build_cached_conditions(cache_result)

    # The normalized store is the preferred cache. When it has no recent SST,
    # use the newest local Copernicus thetao NetCDF cache produced by the data
    # pipeline. This is still provider data; it is explicitly labeled as a
    # cached near-surface model temperature proxy rather than live sensor SST.
    if "sst_c" not in cached_conditions:
        local_sst = get_cached_copernicus_sst(
            latitude=float(location["latitude"]),
            longitude=float(location["longitude"]),
            max_distance_km=_LOCAL_SST_MAX_DISTANCE_KM,
            max_depth_m=_LOCAL_SST_MAX_DEPTH_M,
        )
        if local_sst is not None:
            cached_conditions["sst_c"] = float(local_sst["sst_c"])
            cached_contributions.append(
                {
                    "provider": "Copernicus Marine local NetCDF cache",
                    "source": local_sst.get("source", "Copernicus Marine"),
                    "dataset": local_sst.get("dataset_id", "thetao"),
                    "type": local_sst.get(
                        "data_type",
                        "cached_copernicus_forecast",
                    ),
                    "variables": ["sst_c"],
                    "timestamp": local_sst.get("timestamp"),
                    "distance_km": local_sst.get("distance_km"),
                    "depth_m": local_sst.get("depth_m"),
                    "file": local_sst.get("file"),
                }
            )

    if isinstance(marine_data, dict) and cached_conditions:
        metadata = dict(marine_data.get("metadata") or {})
        metadata["cached_marine_variables"] = sorted(cached_conditions)
        metadata["cache_max_age_days"] = _MARINE_CACHE_MAX_AGE_DAYS
        marine_data = {
            **marine_data,
            **cached_conditions,
            "metadata": metadata,
        }

    live_contributions = marine_result.get("provider_contributions", [])
    provider_contributions = [
        contribution
        for contribution in live_contributions
        if isinstance(contribution, dict)
    ] + cached_contributions

    resolved_variables = (
        set(marine_data.keys())
        if isinstance(marine_data, dict)
        else set()
    )
    missing_variables = [
        variable
        for variable in requested_variables
        if variable not in resolved_variables
    ]

    marine_status = marine_result.get("status", "unavailable")
    marine_agent_result: dict[str, Any] = {
        "agent": "ocean",
        "status": marine_status,
        "source": (
            marine_data.get("source")
            if isinstance(marine_data, dict)
            else "marine provider"
        ),
        "dataset": (
            marine_data.get("dataset")
            if isinstance(marine_data, dict)
            else "marine data"
        ),
        "requested_variables": requested_variables,
        "live_variables": list(_LIVE_MARINE_VARIABLES),
        "cached_variables": sorted(cached_conditions),
        "cache_max_age_days": _MARINE_CACHE_MAX_AGE_DAYS,
        "missing_variables": missing_variables,
        "provider_contributions": provider_contributions,
        "errors": marine_result.get("errors", []),
    }

    if isinstance(marine_data, dict):
        marine_agent_result["conditions"] = marine_data
        updates["evidence"].append(marine_data)

    updates["agent_results"].append(marine_agent_result)

    if is_fishing_query:
        pfz_tool = tool_registry.get("get_pfz_advisory")

        pfz_result = pfz_tool(
            language=state.get("language", "en")
        )

        pfz_agent_result = {
            "agent": "ocean",
            "capability": "pfz",
            "status": pfz_result.get("status", "unavailable"),
            "source": pfz_result.get("source", "INCOIS"),
            "dataset": pfz_result.get("dataset", "PFZ Text Advisory"),
            "advisory_date": pfz_result.get("advisory_date"),
            "valid_until": pfz_result.get("valid_until"),
            "locations": pfz_result.get("locations", []),
            "pfz_available": pfz_result.get("pfz_available", False),
            "quality": pfz_result.get("quality"),
            "warning": pfz_result.get("location_warning"),
            "webgis_url": pfz_result.get("webgis_url"),
            "text_url": pfz_result.get("text_url"),
            "errors": (
                [pfz_result["error"]]
                if pfz_result.get("error")
                else []
            ),
        }

        updates["agent_results"].append(pfz_agent_result)
        updates["evidence"].append(pfz_result)

        if pfz_result.get("error"):
            updates["errors"].append(
                f"INCOIS PFZ: {pfz_result['error']}"
            )

    if marine_result.get("errors"):
        updates["errors"].extend(
            [
                f"{item.get('source', 'marine')}: "
                f"{item.get('error', 'provider error')}"
                for item in marine_result["errors"]
                if isinstance(item, dict)
            ]
        )

    return updates
