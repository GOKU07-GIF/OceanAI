from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database.base import Base


class SensorReading(Base):
    """
    Stores every sensor reading.
    """

    __tablename__ = "sensor_readings"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    sensor_device_id = Column(
        Integer,
        ForeignKey("sensor_devices.id"),
        nullable=False,
    )

    temperature = Column(
        Float,
        nullable=False,
    )

    ph = Column(
        Float,
        nullable=False,
    )

    salinity = Column(
        Float,
        nullable=False,
    )

    oxygen = Column(
        Float,
        nullable=False,
    )

    turbidity = Column(
        Float,
        nullable=False,
        default=0,
    )

    water_quality = Column(
        Float,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    device = relationship(
        "SensorDevice",
        back_populates="readings",
    )