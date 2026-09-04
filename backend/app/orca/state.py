from __future__ import annotations

from typing import Any, Annotated, TypedDict
import operator


class ORCAState(TypedDict, total=False):
    """Shared state passed between ORCA graph nodes.

    ``db`` is request-scoped runtime context for the current graph invocation.
    It is intentionally not persisted as conversation data.
    """

    conversation_id: str
    user_id: int
    query: str
    language: str
    location: dict[str, float]
    requested_time: dict[str, str]
    activity: str
    plan: list[dict[str, Any]]
    agent_results: Annotated[list[dict[str, Any]], operator.add]
    evidence: Annotated[list[dict[str, Any]], operator.add]
    risk_assessment: dict[str, Any]
    recommendation: dict[str, Any]
    map_data: dict[str, Any]
    errors: Annotated[list[str], operator.add]
    db: Any
