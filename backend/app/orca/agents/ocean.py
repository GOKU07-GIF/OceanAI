from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.orca.state import ORCAState
from app.orca.tools.ocean import get_ocean_conditions


def run_ocean_agent(state: ORCAState) -> dict[str, Any]:
    """Retrieve nearby OceanAI observations when the planner requests ocean data."""
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

    result = get_ocean_conditions(
        db=db,
        latitude=location["latitude"],
        longitude=location["longitude"],
        owner_id=state["user_id"],
    )

    agent_result = {
        "agent": "ocean",
        "status": result.get("status", "error"),
        "source": result.get("source", "OceanAI PostgreSQL"),
        "dataset": result.get("dataset", "OceanData"),
        "observation_count": result.get("observation_count", 0),
        "observations": result.get("observations", []),
    }

    updates: dict[str, Any] = {
        "agent_results": [agent_result],
    }

    if result.get("status") == "success":
        updates["evidence"] = [
            {
                "source": result.get("source"),
                "dataset": result.get("dataset"),
                "type": result.get("type"),
                "location": result.get("location"),
                "radius_km": result.get("radius_km"),
                "observations": result.get("observations", []),
            }
        ]

    return updates
