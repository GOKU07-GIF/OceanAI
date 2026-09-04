from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.orca.agents.decision import run_decision_agent
from app.orca.agents.geo import run_geo_agent
from app.orca.agents.ocean import run_ocean_agent
from app.orca.agents.planner import plan_query
from app.orca.agents.response import run_response_agent
from app.orca.agents.risk import run_risk_agent
from app.orca.agents.weather import run_weather_agent
from app.orca.state import ORCAState


_SPECIALISTS = {
    "weather": run_weather_agent,
    "ocean": run_ocean_agent,
    "geo": run_geo_agent,
}


def execute_selected_agents(state: ORCAState) -> dict[str, Any]:
    """Execute only agents selected by the planner and merge their results.

    The first vertical slice remains deterministic and sequential so every
    specialist completes before the shared evidence reaches the risk stage.
    """
    working_state: ORCAState = dict(state)
    updates: dict[str, Any] = {
        "agent_results": [],
        "evidence": [],
        "errors": [],
    }

    selected_agents = [task.get("agent") for task in state.get("plan", [])]

    for agent_name in ("weather", "ocean", "geo"):
        if agent_name not in selected_agents:
            continue

        agent_update = _SPECIALISTS[agent_name](working_state)

        for key, value in agent_update.items():
            if key in {"agent_results", "evidence", "errors"}:
                current = working_state.get(key, [])
                merged = list(current)
                merged.extend(value or [])
                working_state[key] = merged
                updates[key] = merged
            else:
                working_state[key] = value
                updates[key] = value

    return updates


def build_orca_graph():
    """Build the complete first ORCA conversational decision-support slice."""
    graph = StateGraph(ORCAState)
    graph.add_node("planner", plan_query)
    graph.add_node("specialists", execute_selected_agents)
    graph.add_node("risk", run_risk_agent)
    graph.add_node("decision", run_decision_agent)
    graph.add_node("response", run_response_agent)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "specialists")
    graph.add_edge("specialists", "risk")
    graph.add_edge("risk", "decision")
    graph.add_edge("decision", "response")
    graph.add_edge("response", END)

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
