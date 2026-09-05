from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.core.config import settings


# ============================================================
# IMPORT ALL MODELS
# ============================================================

# These imports are required so SQLAlchemy registers all models
# with Base.metadata before create_all() runs.

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.ocean_data import OceanData
from app.models.ocean_observation import OceanObservation
from app.models.sensor_device import SensorDevice
from app.models.sensor_reading import SensorReading
from app.models.sos import SOS
from app.models.alert import Alert


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# CREATE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
