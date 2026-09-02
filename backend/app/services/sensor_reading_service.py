from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.anomaly_detector import detect_anomaly
from app.models.alert import Alert
from app.models.ocean_data import OceanData
from app.models.sensor_reading import SensorReading
from app.models.user import User
from app.repositories.alert_repository import AlertRepository
from app.repositories.sensor_device_repository import SensorDeviceRepository
from app.repositories.sensor_reading_repository import SensorReadingRepository


def create_reading(
    db: Session,
    sensor_device_id: int,
    temperature: float,
    ph: float,
    salinity: float,
    oxygen: float,
    turbidity: float,
    water_quality: float,
    current_user: User,
):
    device = SensorDeviceRepository.get_by_id(db, sensor_device_id)

    if device is None:
        raise HTTPException(status_code=404, detail="Sensor device not found")

    if device.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this sensor device")

    if not device.is_active:
        raise HTTPException(status_code=400, detail="Sensor device is inactive")

    reading = SensorReading(
        sensor_device_id=sensor_device_id,
        temperature=temperature,
        ph=ph,
        salinity=salinity,
        oxygen=oxygen,
        turbidity=turbidity,
        water_quality=water_quality,
    )
    reading = SensorReadingRepository.create(db, reading)

    # Feed the existing OceanData-based dashboard, map and analytics from real sensor observations.
    ocean_data = OceanData(
        latitude=device.latitude,
        longitude=device.longitude,
        temperature=temperature,
        ph=ph,
        salinity=salinity,
        oxygen=oxygen,
        is_active=True,
        owner_id=current_user.id,
    )
    db.add(ocean_data)
    db.commit()

    # Run anomaly rules immediately after ingestion and create a user alert when required.
    anomaly = detect_anomaly(
        temperature=temperature,
        ph=ph,
        salinity=salinity,
        dissolved_oxygen=oxygen,
    )

    if anomaly["status"] == "Alert":
        severity = "CRITICAL" if len(anomaly["alerts"]) >= 2 else "HIGH"
        alert = Alert(
            title="Ocean Sensor Anomaly",
            message="; ".join(anomaly["alerts"]),
            alert_type="WARNING",
            severity=severity,
            user_id=current_user.id,
            is_read=False,
        )
        AlertRepository.create(db, alert)

    return reading


def latest_readings(
    db: Session,
    current_user: User,
):
    return SensorReadingRepository.get_latest(
        db,
        owner_id=current_user.id,
    )
