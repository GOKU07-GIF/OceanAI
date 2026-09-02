from sqlalchemy.orm import Session

from app.models.sensor_device import SensorDevice
from app.models.sensor_reading import SensorReading


class SensorReadingRepository:

    @staticmethod
    def create(
        db: Session,
        reading: SensorReading,
    ):
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return reading

    @staticmethod
    def get_latest(
        db: Session,
        owner_id: int,
        limit: int = 100,
    ):
        return (
            db.query(SensorReading)
            .join(SensorDevice, SensorReading.sensor_device_id == SensorDevice.id)
            .filter(SensorDevice.owner_id == owner_id)
            .order_by(SensorReading.created_at.desc())
            .limit(limit)
            .all()
        )
