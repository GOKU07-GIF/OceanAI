from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading

from app.repositories.sensor_device_repository import (
    SensorDeviceRepository,
)

from app.repositories.sensor_reading_repository import (
    SensorReadingRepository,
)


def create_reading(
    db: Session,
    sensor_device_id: int,
    temperature: float,
    ph: float,
    salinity: float,
    oxygen: float,
    turbidity: float,
    water_quality: float,
):

    device = SensorDeviceRepository.get_by_id(
        db,
        sensor_device_id,
    )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor device not found",
        )

    reading = SensorReading(
        sensor_device_id=sensor_device_id,
        temperature=temperature,
        ph=ph,
        salinity=salinity,
        oxygen=oxygen,
        turbidity=turbidity,
        water_quality=water_quality,
    )

    return SensorReadingRepository.create(
        db,
        reading,
    )


def latest_readings(
    db: Session,
):

    return SensorReadingRepository.get_latest(
        db,
    )