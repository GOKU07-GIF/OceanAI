from sqlalchemy.orm import Session

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
        limit: int = 100,
    ):

        return (
            db.query(SensorReading)
            .order_by(
                SensorReading.created_at.desc()
            )
            .limit(limit)
            .all()
        )