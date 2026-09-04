from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState


def plan_query(state: ORCAState) -> dict[str, Any]:
    """Create a small, deterministic task plan for the first ORCA slice.

    This is intentionally LLM-free. It establishes the graph/state contract
    first; an LLM planner can be added behind the same interface later.
    """
    query = state.get("query", "").lower()

    tasks: list[dict[str, str]] = []
    activity = "general_marine_information"

    fishing_terms = ("fishing", "fish", "pfz", "fishing zone")
    safety_terms = ("safe", "safety", "danger", "hazard", "risk")
    weather_terms = ("weather", "wind", "rain", "storm", "lightning", "cyclone")
    ocean_terms = ("ocean", "wave", "swell", "current", "sst", "sea", "chlorophyll")
    route_terms = ("route", "navigate", "navigation", "direction")

    if any(term in query for term in fishing_terms):
        activity = "fishing"
        tasks.append({
            "agent": "ocean",
            "reason": "Fishing-related queries may require marine conditions and PFZ information.",
        })

    if any(term in query for term in safety_terms):
        activity = "marine_safety"
        tasks.append({
            "agent": "weather",
            "reason": "Safety assessment requires forecast and hazard information.",
        })
        tasks.append({
            "agent": "ocean",
            "reason": "Safety assessment requires sea-state and ocean conditions.",
        })

    if any(term in query for term in weather_terms) and not any(t["agent"] == "weather" for t in tasks):
        tasks.append({
            "agent": "weather",
            "reason": "The query explicitly asks for weather or atmospheric conditions.",
        })

    if any(term in query for term in ocean_terms) and not any(t["agent"] == "ocean" for t in tasks):
        tasks.append({
            "agent": "ocean",
            "reason": "The query explicitly asks for ocean or sea-state information.",
        })

    if any(term in query for term in route_terms) or "near" in query or "location" in query:
        tasks.append({
            "agent": "geo",
            "reason": "The query requires location, distance, boundary or route context.",
        })

    if activity in {"fishing", "marine_safety"} or len(tasks) > 1:
        if not any(t["agent"] == "geo" for t in tasks):
            tasks.append({
                "agent": "geo",
                "reason": "Marine decisions need spatial context for the selected location.",
            })

    if not tasks:
        tasks.append({
            "agent": "ocean",
            "reason": "Default marine information lookup for an unspecified query.",
        })

    return {
        "activity": activity,
        "plan": tasks,
    }
