from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.orca.agents.geo import run_geo_agent
from app.orca.agents.ocean import run_ocean_agent
from app.orca.agents.planner import plan_query
from app.orca.agents.weather import run_weather_agent
from app.orca.state import ORCAState


def route_after_planner(state: ORCAState) -> list[str] | str:
    """Run every specialized agent selected by the planner."""
    agents = {task.get("agent") for task in state.get("plan", [])}
    selected = [
        agent
        for agent in ("weather", "ocean", "geo")
        if agent in agents
    ]
    return selected if selected else "end"


def build_orca_graph():
    """Build the executable ORCA graph slice with parallel specialist routing."""
    graph = StateGraph(ORCAState)
    graph.add_node("planner", plan_query)
    graph.add_node("weather", run_weather_agent)
    graph.add_node("ocean", run_ocean_agent)
    graph.add_node("geo", run_geo_agent)

    graph.add_edge(START, "planner")
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "weather": "weather",
            "ocean": "ocean",
            "geo": "geo",
            "end": END,
        },
    )
    graph.add_edge("weather", END)
    graph.add_edge("ocean", END)
    graph.add_edge("geo", END)

    return graph.compile()


orca_graph = build_orca_graph()


def run_orca_plan(
    *,
    query: str,
    user_id: int,
    location: dict[str, float] | None = None,
    language: str = "en",
    conversation_id: str = "",
    db: Any = None,
) -> ORCAState:
    state: ORCAState = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "query": query,
        "language": language,
    }

    if location is not None:
        state["location"] = location

    if db is not None:
        state["db"] = db

    return orca_graph.invoke(state)
