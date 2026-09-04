from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState
from app.orca.tools.geo import reverse_geocode


def run_geo_agent(state: ORCAState) -> dict[str, Any]:
    """Resolve the user's coordinates into auditable geospatial context."""
    location = state.get("location")
    if not location:
        return {
            "agent_results": [
                {
                    "agent": "geo",
                    "status": "error",
                    "error": "Location is required for geospatial intelligence.",
                }
            ],
            "errors": ["Geo agent could not run because location is missing."],
        }

    result = reverse_geocode(
        latitude=location["latitude"],
        longitude=location["longitude"],
    )

    agent_result = {
        "agent": "geo",
        "status": result.get("status", "error"),
        "source": result.get("source", "OpenStreetMap Nominatim"),
        "dataset": result.get("dataset", "Reverse Geocoding"),
        "location": result.get("location"),
        "note": result.get("note"),
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
                "retrieved_at": result.get("retrieved_at"),
                "note": result.get("note"),
            }
        ]
        updates["map_data"] = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "display_name": result.get("location", {}).get("display_name"),
        }

    if result.get("error"):
        agent_result["error"] = result["error"]
        updates["errors"] = [result["error"]]

    return updates
