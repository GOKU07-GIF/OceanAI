from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, String, UniqueConstraint

from app.database.base import Base


class OceanObservation(Base):
    """Normalized observation/model value produced by the data ingestion layer."""

    __tablename__ = "ocean_observations"
    __table_args__ = (
        UniqueConstraint(
            "timestamp",
            "latitude",
            "longitude",
            "variable",
            "source",
            "dataset",
            name="uq_ocean_observation_identity",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    depth_m = Column(Float, nullable=True)
    variable = Column(String(64), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=True)
    source = Column(String(64), nullable=False, index=True)
    dataset = Column(String(160), nullable=False)
    data_type = Column(String(32), nullable=False)
    quality_flag = Column(String(32), nullable=False, default="present")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
