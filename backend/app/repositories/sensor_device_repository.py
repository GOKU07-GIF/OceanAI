from sqlalchemy.orm import Session

from app.models.sensor_device import SensorDevice


class SensorDeviceRepository:

    @staticmethod
    def get_by_device_id(
        db: Session,
        device_id: str,
    ):
        return (
            db.query(SensorDevice)
            .filter(
                SensorDevice.device_id == device_id
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        device: SensorDevice,
    ):

        db.add(device)

        db.commit()

        db.refresh(device)

        return device

    @staticmethod
    def get_all(
        db: Session,
    ):
        return db.query(
            SensorDevice
        ).all()

    @staticmethod
    def get_by_id(
        db: Session,
        device_id: int,
    ):
        return (
            db.query(SensorDevice)
            .filter(
                SensorDevice.id == device_id
            )
            .first()
        )