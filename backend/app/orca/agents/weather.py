from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState
from app.orca.tools.registry import tool_registry


def run_weather_agent(state: ORCAState) -> dict[str, Any]:
    """Execute weather retrieval only when the planner requested weather."""
    location = state.get("location")
    if not location:
        return {
            "agent_results": [
                {
                    "agent": "weather",
                    "status": "error",
                    "error": "Location is required for weather intelligence.",
                }
            ],
            "errors": ["Weather agent could not run because location is missing."],
        }

    get_weather_forecast = tool_registry.get("get_weather_forecast")
    result = get_weather_forecast(
        latitude=location["latitude"],
        longitude=location["longitude"],
        days=2,
    )

    agent_result = {
        "agent": "weather",
        "status": result.get("status", "error"),
        "source": result.get("source", "WeatherAPI"),
        "evidence": result.get("evidence"),
    }

    updates: dict[str, Any] = {
        "agent_results": [agent_result],
    }

    if result.get("evidence"):
        updates["evidence"] = [result["evidence"]]

    if result.get("error"):
        updates["errors"] = [result["error"]]
        agent_result["error"] = result["error"]

    return updates
