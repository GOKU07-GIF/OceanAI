from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
)

from sqlalchemy.orm import relationship

from app.database.base import Base

class OceanData(Base):
    __tablename__ = "ocean_data"

    id = Column(Integer, primary_key=True, index=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    temperature = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    salinity = Column(Float, nullable=False)
    oxygen = Column(Float, nullable=False)

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    owner = relationship(
        "User",
        back_populates="ocean_data",
    )