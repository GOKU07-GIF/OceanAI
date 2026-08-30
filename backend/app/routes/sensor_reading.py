from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

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
    )


@router.get(
    "",
    response_model=list[SensorReadingResponse],
)
def get_readings(
    db: Session = Depends(get_db),
):

    return latest_readings(
        db,
    )