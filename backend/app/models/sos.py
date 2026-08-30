from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    String,
)

from sqlalchemy.orm import relationship

from app.database.base import Base


class SOS(Base):
    __tablename__ = "sos_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    latitude = Column(
        Float,
        nullable=False,
    )

    longitude = Column(
        Float,
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    station_id = Column(
        Integer,
        ForeignKey("ocean_data.id"),
        nullable=True,
    )

    status = Column(
        String(20),
        default="ACTIVE",
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
    )

    station = relationship(
        "OceanData",
    )

    @property
    def station_distance_km(self):
        """
        Calculate distance between the SOS location
        and the assigned ocean station.
        """

        if self.station is None:
            return None

        from math import radians, sin, cos, sqrt, atan2

        earth_radius = 6371.0

        lat1 = radians(self.latitude)
        lon1 = radians(self.longitude)

        lat2 = radians(self.station.latitude)
        lon2 = radians(self.station.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1)
            * cos(lat2)
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        return round(earth_radius * c, 2)