from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

from app.orca.state import ORCAState


_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_ENV_FILE)

DEFAULT_MODEL = os.getenv("ORCA_GEMINI_MODEL", "gemini-3.8-flash")

_SYSTEM_INSTRUCTIONS = """You are ORCA, a marine decision-support assistant.

Your job is to turn an already-computed ORCA assessment into a clear user-facing response.
Do not invent marine facts, sources, measurements, warnings, routes, or safer alternatives.
Do not override the deterministic risk assessment or claim certainty that the evidence does not support.
When evidence is missing, say so plainly.
Do not reveal hidden chain-of-thought or internal reasoning. Give a concise explanation based only on the supplied evidence, factors, and limitations.
Respect the requested language when practical. Keep safety recommendations conservative.
"""


def _fallback_response(state: ORCAState) -> str:
    recommendation = state.get("recommendation") or {}
    risk = state.get("risk_assessment") or {}
    factors = list(recommendation.get("factors") or risk.get("factors") or [])
    limitations = list(recommendation.get("limitations") or risk.get("limitations") or [])

    decision = recommendation.get("decision", "INSUFFICIENT_EVIDENCE")
    text = recommendation.get(
        "recommendation",
        "A reliable marine recommendation cannot be made from the available evidence.",
    )

    lines = [
        f"{text}",
        f"Risk level: {recommendation.get('risk_level', risk.get('overall_risk', 'UNKNOWN'))}.",
    ]
    if factors:
        lines.append("Key factors: " + "; ".join(factors[:3]) + ".")
    if limitations:
        lines.append("Limitations: " + "; ".join(limitations[:3]) + ".")
    if decision == "INSUFFICIENT_EVIDENCE":
        lines.append("Verify the missing marine data before making a departure or navigation decision.")
    return " ".join(lines)


def run_response_agent(state: ORCAState) -> dict[str, Any]:
    """Create a concise conversational answer from structured ORCA results.

    Gemini is used only as the presentation/reasoning-explanation layer. The
    numerical risk and decision are computed upstream by deterministic agents.
    """
    payload = {
        "query": state.get("query", ""),
        "language": state.get("language", "en"),
        "location": state.get("location"),
        "activity": state.get("activity"),
        "requested_time": state.get("requested_time"),
        "risk_assessment": state.get("risk_assessment", {}),
        "recommendation": state.get("recommendation", {}),
        "evidence": state.get("evidence", []),
    }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "assistant_response": _fallback_response(state),
            "response_source": "deterministic_fallback",
        }

    try:
        client = genai.Client(api_key=api_key)
        interaction = client.interactions.create(
            model=DEFAULT_MODEL,
            system_instruction=_SYSTEM_INSTRUCTIONS,
            input=json.dumps(payload, ensure_ascii=False, default=str),
            store=False,
        )
        text = (interaction.output_text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response")

        return {
            "assistant_response": text,
            "response_source": "gemini",
        }
    except Exception as exc:
        return {
            "assistant_response": _fallback_response(state),
            "response_source": "deterministic_fallback",
            "errors": [f"Conversational layer fallback: {exc}"],
        }
