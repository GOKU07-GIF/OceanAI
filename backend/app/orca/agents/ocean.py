from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.orca.marine.models import MarineDataRequest
from app.orca.marine.provider import marine_provider
from app.orca.state import ORCAState
from app.orca.tools.ocean import get_ocean_conditions
from app.orca.tools.registry import tool_registry


_MARINE_SAFETY_VARIABLES = [
    "sst_c",
    "wave_height_m",
    "wave_period_s",
]

_MARINE_FISHING_VARIABLES = [
    "sst_c",
    "wave_height_m",
    "wave_period_s",
    "chlorophyll_mg_m3",
]


_FISHING_TERMS = ("fishing", "fish", "pfz", "fishing zone")


def run_ocean_agent(state: ORCAState) -> dict[str, Any]:
    """Collect local observations plus authoritative marine-source context."""
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
        _MARINE_FISHING_VARIABLES if is_fishing_query else _MARINE_SAFETY_VARIABLES
    )

    updates: dict[str, Any] = {
        "agent_results": [],
        "evidence": [],
        "errors": [],
    }

    local_result = get_ocean_conditions(
        db=db,
        latitude=location["latitude"],
        longitude=location["longitude"],
        owner_id=state["user_id"],
    )

    local_agent_result = {
        "agent": "ocean",
        "status": local_result.get("status", "error"),
        "source": local_result.get("source", "OceanAI PostgreSQL"),
        "dataset": local_result.get("dataset", "OceanData"),
        "observation_count": local_result.get("observation_count", 0),
        "observations": local_result.get("observations", []),
    }
    updates["agent_results"].append(local_agent_result)

    if local_result.get("status") == "success":
        updates["evidence"].append(
            {
                "source": local_result.get("source"),
                "dataset": local_result.get("dataset"),
                "type": local_result.get("type"),
                "location": local_result.get("location"),
                "radius_km": local_result.get("radius_km"),
                "observations": local_result.get("observations", []),
            }
        )

    marine_request: MarineDataRequest = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "variables": requested_variables,
        "radius_km": 50.0,
    }

    if state.get("requested_time"):
        requested_time = state["requested_time"]
        if requested_time.get("start"):
            marine_request["start_time"] = requested_time["start"]
        if requested_time.get("end"):
            marine_request["end_time"] = requested_time["end"]

    marine_result = marine_provider.fetch(
        request=marine_request,
        provider_order=(
            "incois",
            "copernicus",
            "copernicus_chlorophyll",
            "mosdac",
        ),
    )

    marine_data = marine_result.get("data")
    marine_agent_result: dict[str, Any] = {
        "agent": "ocean",
        "status": marine_result.get("status", "unavailable"),
        "source": marine_data.get("source") if isinstance(marine_data, dict) else "marine provider",
        "dataset": marine_data.get("dataset") if isinstance(marine_data, dict) else "marine data",
        "requested_variables": requested_variables,
        "missing_variables": marine_result.get("missing_variables", []),
        "provider_contributions": marine_result.get("provider_contributions", []),
        "errors": marine_result.get("errors", []),
    }
    if isinstance(marine_data, dict):
        marine_agent_result["conditions"] = marine_data

    updates["agent_results"].append(marine_agent_result)

    if isinstance(marine_data, dict):
        updates["evidence"].append(marine_data)

    # PFZ is an official advisory service. Return exact point data when the
    # public response exposes it; otherwise preserve advisory metadata and a
    # warning rather than inferring a fishing location.
    if is_fishing_query:
        pfz_tool = tool_registry.get("get_pfz_advisory")
        pfz_result = pfz_tool(language=state.get("language", "en"))
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
            "errors": [pfz_result["error"]] if pfz_result.get("error") else [],
        }
        updates["agent_results"].append(pfz_agent_result)
        updates["evidence"].append(pfz_result)
        if pfz_result.get("error"):
            updates["errors"].append(f"INCOIS PFZ: {pfz_result['error']}")

    if marine_result.get("errors"):
        updates["errors"].extend(
            [
                f"{item.get('source', 'marine')}: {item.get('error', 'provider error')}"
                for item in marine_result["errors"]
                if isinstance(item, dict)
            ]
        )

    return updates
