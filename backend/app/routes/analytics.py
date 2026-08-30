from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.services.analytics_service import (
    temperature_trend,
    ph_trend,
    location_summary,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/temperature")
def get_temperature(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return temperature_trend(db)


@router.get("/ph")
def get_ph(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ph_trend(db)


@router.get("/locations")
def get_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return location_summary(db)