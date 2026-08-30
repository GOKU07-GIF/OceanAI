from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database.base import Base


class SensorDevice(Base):
    """
    Physical IoT Sensor Device.
    """

    __tablename__ = "sensor_devices"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    device_name = Column(
        String(100),
        nullable=False,
    )

    device_type = Column(
        String(50),
        nullable=False,
    )

    latitude = Column(
        Float,
        nullable=False,
    )

    longitude = Column(
        Float,
        nullable=False,
    )

    firmware_version = Column(
        String(30),
        default="1.0.0",
    )

    battery_level = Column(
        Float,
        default=100,
    )

    status = Column(
        String(20),
        default="ONLINE",
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    owner = relationship("User")

    readings = relationship(
        "SensorReading",
        back_populates="device",
        cascade="all, delete-orphan",
    )