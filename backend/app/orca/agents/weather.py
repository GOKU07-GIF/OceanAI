from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState
from app.orca.tools.registry import tool_registry


def run_weather_agent(state: ORCAState) -> dict[str, Any]:
    """Execute weather retrieval for the planner's requested time window."""
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
    requested_time = state.get("requested_time", {})

    result = get_weather_forecast(
        latitude=location["latitude"],
        longitude=location["longitude"],
        days=2,
        start_time=requested_time.get("start"),
        end_time=requested_time.get("end"),
    )

    agent_result = {
        "agent": "weather",
        "status": result.get("status", "error"),
        "source": result.get("source", "WeatherAPI"),
        "requested_window": requested_time or None,
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
