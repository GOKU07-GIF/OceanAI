from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.orca.state import ORCAState


_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_ENV_FILE)

DEFAULT_MODEL = os.getenv("ORCA_LLM_MODEL", "gpt-5")

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

    lines = [f"{text}", f"Risk level: {recommendation.get('risk_level', risk.get('overall_risk', 'UNKNOWN'))}."]
    if factors:
        lines.append("Key factors: " + "; ".join(factors[:3]) + ".")
    if limitations:
        lines.append("Limitations: " + "; ".join(limitations[:3]) + ".")
    if decision == "INSUFFICIENT_EVIDENCE":
        lines.append("Verify the missing marine data before making a departure or navigation decision.")
    return " ".join(lines)


def run_response_agent(state: ORCAState) -> dict[str, Any]:
    """Create a concise conversational answer from structured ORCA results.

    The LLM is a presentation/reasoning-explanation layer only. The numerical
    risk and decision are computed upstream by deterministic agents.
    """
    payload = {
        "query": state.get("query", ""),
        "language": state.get("language", "en"),
        "location": state.get("location"),
        "activity": state.get("activity"),
        "risk_assessment": state.get("risk_assessment", {}),
        "recommendation": state.get("recommendation", {}),
        "evidence": state.get("evidence", []),
    }

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ORCA_OPENAI_API_KEY")
    if not api_key:
        return {
            "assistant_response": _fallback_response(state),
            "response_source": "deterministic_fallback",
        }

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=DEFAULT_MODEL,
            instructions=_SYSTEM_INSTRUCTIONS,
            input=json.dumps(payload, ensure_ascii=False, default=str),
            store=False,
        )
        text = (response.output_text or "").strip()
        if not text:
            raise RuntimeError("LLM returned an empty response")

        return {
            "assistant_response": text,
            "response_source": "openai",
        }
    except Exception as exc:
        return {
            "assistant_response": _fallback_response(state),
            "response_source": "deterministic_fallback",
            "errors": [f"Conversational layer fallback: {exc}"],
        }
