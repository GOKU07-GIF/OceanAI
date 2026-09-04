from __future__ import annotations

from typing import Any

from app.orca.state import ORCAState


def _has_missing_safety_dimension(limitations: list[str]) -> bool:
    """Return True when safety-critical evidence is incomplete."""
    safety_markers = (
        "wave",
        "swell",
        "maritime restriction",
        "geofence",
        "vessel-specific",
        "marine forecast evidence",
    )
    return any(
        any(marker in text.lower() for marker in safety_markers)
        for text in limitations
    )


def run_decision_agent(state: ORCAState) -> dict[str, Any]:
    """Convert deterministic risk assessment into an actionable decision.

    The decision layer never treats missing safety-critical dimensions as safe
    and never invents alternative times/locations without supporting evidence.
    """
    risk = state.get("risk_assessment") or {}
    level = str(risk.get("overall_risk", "UNKNOWN")).upper()
    limitations = list(risk.get("limitations") or [])
    factors = list(risk.get("factors") or [])
    activity = state.get("activity", "general_marine_information")
    requested_time = state.get("requested_time")

    safety_dimensions_missing = _has_missing_safety_dimension(limitations)

    if level == "CRITICAL":
        decision = "DO_NOT_RECOMMEND"
        recommendation = "Do not proceed with the planned marine activity based on the current risk assessment."
    elif level == "HIGH":
        decision = "DO_NOT_RECOMMEND"
        recommendation = "Do not proceed with the planned marine activity under the currently assessed conditions."
    elif level == "MODERATE":
        decision = "CAUTION"
        recommendation = "Conditions require caution; verify all missing marine safety dimensions before making a departure decision."
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
            "requested_window": requested_time,
            "recommendation": recommendation,
            "factors": factors,
            "limitations": limitations,
        }
    }
