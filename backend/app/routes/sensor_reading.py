from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.sensor_reading_schema import (
    SensorReadingCreate,
    SensorReadingResponse,
)
from app.services.sensor_reading_service import (
    create_reading,
    latest_readings,
)

router = APIRouter(
    prefix="/readings",
    tags=["Sensor Readings"],
)


@router.post(
    "",
    response_model=SensorReadingResponse,
)
def add_reading(
    reading: SensorReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_reading(
        db=db,
        sensor_device_id=reading.sensor_device_id,
        temperature=reading.temperature,
        ph=reading.ph,
        salinity=reading.salinity,
        oxygen=reading.oxygen,
        turbidity=reading.turbidity,
        water_quality=reading.water_quality,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[SensorReadingResponse],
)
def get_readings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return latest_readings(db, current_user=current_user)
