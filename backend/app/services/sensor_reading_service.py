from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.anomaly_detector import detect_anomaly
from app.ai.predictor import predict_water_quality
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

    try:
        ai_result = predict_water_quality(
            temperature=temperature,
            ph=ph,
            salinity=salinity,
            dissolved_oxygen=oxygen,
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
        reading = SensorReadingRepository.create(db, reading)

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

        anomaly = detect_anomaly(
            temperature=temperature,
            ph=ph,
            salinity=salinity,
            dissolved_oxygen=oxygen,
        )

        if anomaly["status"] == "Alert":
            severity = "CRITICAL" if len(anomaly["alerts"]) >= 2 else "HIGH"
            AlertRepository.create(
                db,
                Alert(
                    title=f"Ocean Sensor Anomaly - {ai_result['water_quality']}",
                    message=(
                        f"AI assessment: {ai_result['recommendation']} "
                        f"Detected: {'; '.join(anomaly['alerts'])}"
                    ),
                    alert_type="WARNING",
                    severity=severity,
                    user_id=current_user.id,
                    is_read=False,
                ),
            )

        db.commit()
        db.refresh(reading)
        return reading

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process sensor reading: {exc}",
        ) from exc


def latest_readings(
    db: Session,
    current_user: User,
):
    return SensorReadingRepository.get_latest(
        db,
        owner_id=current_user.id,
    )
