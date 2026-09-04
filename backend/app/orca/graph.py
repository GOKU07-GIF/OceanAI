from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.orca.agents.planner import plan_query
from app.orca.state import ORCAState


def build_orca_graph():
    """Build the first ORCA graph slice.

    The graph intentionally contains only the planner node at this stage.
    Specialized agents and verified data tools will be added behind the same
    state contract after their source/access contracts are finalized.
    """
    graph = StateGraph(ORCAState)
    graph.add_node("planner", plan_query)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", END)
    return graph.compile()


orca_graph = build_orca_graph()


def run_orca_plan(
    *,
    query: str,
    user_id: int,
    location: dict[str, float] | None = None,
    language: str = "en",
    conversation_id: str = "",
) -> ORCAState:
    state: ORCAState = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "query": query,
        "language": language,
    }

    if location is not None:
        state["location"] = location

    return orca_graph.invoke(state)
