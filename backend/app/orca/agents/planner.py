from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState


def plan_query(state: ORCAState) -> dict[str, Any]:
    """Create a deterministic task plan for the first ORCA slice.

    The planner establishes the graph/state contract first. An LLM planner can
    later replace the intent classification while preserving this output
    structure.
    """
    query = state.get("query", "").lower()

    tasks: list[dict[str, str]] = []
    activity = "general_marine_information"

    fishing_terms = ("fishing", "fish", "pfz", "fishing zone")
    safety_terms = ("safe", "safety", "danger", "hazard", "risk")
    weather_terms = ("weather", "wind", "rain", "storm", "lightning", "cyclone")
    ocean_terms = ("ocean", "wave", "swell", "current", "sst", "sea", "chlorophyll")
    route_terms = ("route", "navigate", "navigation", "direction")

    def add_task(agent: str, reason: str) -> None:
        if not any(task["agent"] == agent for task in tasks):
            tasks.append({"agent": agent, "reason": reason})

    if any(term in query for term in fishing_terms):
        activity = "fishing"
        add_task(
            "ocean",
            "Fishing-related queries may require marine conditions and PFZ information.",
        )

    if any(term in query for term in safety_terms):
        activity = "marine_safety"
        add_task(
            "weather",
            "Safety assessment requires forecast and hazard information.",
        )
        add_task(
            "ocean",
            "Safety assessment requires sea-state and ocean conditions.",
        )

    if any(term in query for term in weather_terms):
        add_task(
            "weather",
            "The query explicitly asks for weather or atmospheric conditions.",
        )

    if any(term in query for term in ocean_terms):
        add_task(
            "ocean",
            "The query explicitly asks for ocean or sea-state information.",
        )

    if any(term in query for term in route_terms) or "near" in query or "location" in query:
        add_task(
            "geo",
            "The query requires location, distance, boundary or route context.",
        )

    if activity in {"fishing", "marine_safety"} or len(tasks) > 1:
        add_task(
            "geo",
            "Marine decisions need spatial context for the selected location.",
        )

    if not tasks:
        add_task(
            "ocean",
            "Default marine information lookup for an unspecified query.",
        )

    return {
        "activity": activity,
        "plan": tasks,
    }
