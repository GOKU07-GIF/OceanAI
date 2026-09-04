from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState


def run_decision_agent(state: ORCAState) -> dict[str, Any]:
    """Convert the deterministic risk assessment into an actionable decision.

    The decision layer never treats missing safety-critical dimensions as safe.
    It also avoids inventing alternative times/locations when the available
    evidence is insufficient to justify them.
    """
    risk = state.get("risk_assessment") or {}
    level = str(risk.get("overall_risk", "UNKNOWN")).upper()
    limitations = list(risk.get("limitations") or [])
    factors = list(risk.get("factors") or [])
    activity = state.get("activity", "general_marine_information")

    safety_dimensions_missing = any(
        text in limitations
        for text in (
            "Wave and swell conditions are not yet part of this risk calculation.",
            "Maritime restriction/geofence data is not yet part of this risk calculation.",
        )
    )

    if level == "CRITICAL":
        decision = "DO_NOT_RECOMMEND"
        recommendation = "Do not proceed with the planned marine activity based on the current risk assessment."
    elif level == "HIGH":
        decision = "DO_NOT_RECOMMEND"
        recommendation = "Do not proceed with the planned marine activity under the currently assessed conditions."
    elif level == "MODERATE":
        decision = "CAUTION"
        recommendation = "Conditions require caution; verify the missing marine safety dimensions before making a departure decision."
    elif level == "LOW" and not safety_dimensions_missing:
        decision = "RECOMMEND_WITH_CAUTION"
        recommendation = "Current available evidence does not indicate elevated risk, but continue to monitor conditions before departure."
    else:
        decision = "INSUFFICIENT_EVIDENCE"
        recommendation = "A reliable go/no-go recommendation cannot be made yet because important marine safety evidence is missing."

    return {
        "recommendation": {
            "decision": decision,
            "activity": activity,
            "risk_level": level,
            "confidence": risk.get("confidence", "LOW"),
            "recommendation": recommendation,
            "factors": factors,
            "limitations": limitations,
        }
    }
