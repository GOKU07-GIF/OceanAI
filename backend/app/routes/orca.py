from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.orca.graph import run_orca_plan


router = APIRouter(prefix="/orca", tags=["ORCA"])


class ORCAPlanRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    language: str = Field(default="en", min_length=2, max_length=20)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    conversation_id: str = Field(default="", max_length=100)


class ORCAPlanResponse(BaseModel):
    activity: str
    requested_time: dict[str, str] | None = None
    plan: list[dict[str, str]]
    agent_results: list[dict]
    evidence: list[dict]
    risk_assessment: dict
    recommendation: dict
    assistant_response: str
    response_source: str
    errors: list[str]


@router.post("/plan", response_model=ORCAPlanResponse)
def create_orca_plan(
    payload: ORCAPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    location = None
    if payload.latitude is not None and payload.longitude is not None:
        location = {
            "latitude": payload.latitude,
            "longitude": payload.longitude,
        }

    result = run_orca_plan(
        query=payload.query,
        user_id=current_user.id,
        location=location,
        language=payload.language,
        conversation_id=payload.conversation_id,
        db=db,
    )

    return {
        "activity": result.get("activity", "general_marine_information"),
        "requested_time": result.get("requested_time"),
        "plan": result.get("plan", []),
        "agent_results": result.get("agent_results", []),
        "evidence": result.get("evidence", []),
        "risk_assessment": result.get("risk_assessment", {}),
        "recommendation": result.get("recommendation", {}),
        "assistant_response": result.get("assistant_response", ""),
        "response_source": result.get("response_source", "deterministic_fallback"),
        "errors": result.get("errors", []),
    }
