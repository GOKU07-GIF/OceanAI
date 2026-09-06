from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState


def run_decision_agent(state: ORCAState) -> dict[str, Any]:
    """Convert deterministic risk assessment into an actionable decision.

    Only explicit safety blockers prevent a recommendation. Informational
    limitations such as missing vessel-specific constraints or geofences stay
    visible to the user without making every result INSUFFICIENT_EVIDENCE.
    """
    risk = state.get("risk_assessment") or {}
    level = str(
        risk.get(
            "overall_risk",
            "UNKNOWN",
        )
    ).upper()
    limitations = list(
        risk.get("limitations") or []
    )
    factors = list(
        risk.get("factors") or []
    )
    blockers = list(
        risk.get("decision_blockers") or []
    )
    activity = state.get(
        "activity",
        "general_marine_information",
    )
    requested_time = state.get("requested_time")

    if level == "CRITICAL":
        decision = "DO_NOT_RECOMMEND"
        recommendation = (
            "Do not proceed with the planned marine activity based on the "
            "current risk assessment."
        )
    elif level == "HIGH":
        decision = "DO_NOT_RECOMMEND"
        recommendation = (
            "Do not proceed with the planned marine activity under the "
            "currently assessed conditions."
        )
    elif level == "MODERATE":
        decision = "CAUTION"
        recommendation = (
            "Conditions require caution; review the identified risk factors "
            "and verify remaining safety information before departure."
        )
    elif blockers:
        decision = "INSUFFICIENT_EVIDENCE"
        recommendation = (
            "A reliable go/no-go recommendation cannot be made yet because "
            "important marine safety evidence is missing."
        )
    else:
        decision = "RECOMMEND_WITH_CAUTION"
        recommendation = (
            "Available environmental evidence does not indicate elevated "
            "prototype risk. Continue to monitor official conditions and "
            "use normal maritime precautions before departure."
        )

    return {
        "recommendation": {
            "decision": decision,
            "activity": activity,
            "risk_level": level,
            "confidence": risk.get(
                "confidence",
                "LOW",
            ),
            "requested_window": requested_time,
            "recommendation": recommendation,
            "factors": factors,
            "limitations": limitations,
            "decision_blockers": blockers,
        }
    }
