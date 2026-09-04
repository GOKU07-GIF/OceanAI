from __future__ import annotations

from typing import Any, TypedDict


class ORCAState(TypedDict, total=False):
    """Shared state passed between ORCA graph nodes."""

    conversation_id: str
    user_id: int
    query: str
    language: str
    location: dict[str, float]
    requested_time: dict[str, str]
    activity: str
    plan: list[dict[str, Any]]
    agent_results: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    risk_assessment: dict[str, Any]
    recommendation: dict[str, Any]
    map_data: dict[str, Any]
    errors: list[str]
