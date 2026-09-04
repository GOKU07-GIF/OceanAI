from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.orca.agents.planner import plan_query
from app.orca.agents.weather import run_weather_agent
from app.orca.state import ORCAState


def route_after_planner(state: ORCAState) -> str:
    """Run only the specialized agents selected by the planner."""
    agents = {task.get("agent") for task in state.get("plan", [])}
    return "weather" if "weather" in agents else "end"


def build_orca_graph():
    """Build the first executable ORCA graph slice."""
    graph = StateGraph(ORCAState)
    graph.add_node("planner", plan_query)
    graph.add_node("weather", run_weather_agent)

    graph.add_edge(START, "planner")
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "weather": "weather",
            "end": END,
        },
    )
    graph.add_edge("weather", END)

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
