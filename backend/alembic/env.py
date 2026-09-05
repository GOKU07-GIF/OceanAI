from logging.config import fileConfig
from pathlib import Path
import sys

from sqlalchemy import engine_from_config, pool
from alembic import context


# -------------------------------------------------------------------
# Add project root to Python path
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


# -------------------------------------------------------------------
# Import application modules
# -------------------------------------------------------------------

from app.core.config import settings
from app.database.base import Base


# -------------------------------------------------------------------
# Import ALL models so SQLAlchemy registers them with Base.metadata
# -------------------------------------------------------------------

from app.models.user import User
from app.models.ocean_data import OceanData
from app.models.ocean_observation import OceanObservation
from app.models.refresh_token import RefreshToken
from app.models.sos import SOS
from app.models.alert import Alert
from app.models.sensor_device import SensorDevice
from app.models.sensor_reading import SensorReading


# -------------------------------------------------------------------
# Alembic Config
# -------------------------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)


# Tell Alembic about all SQLAlchemy models
target_metadata = Base.metadata


# -------------------------------------------------------------------
# Offline Migrations
# -------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------------------------
# Online Migrations
# -------------------------------------------------------------------

def run_migrations_online() -> None:
    """Run migrations in online mode."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------------------------------------------
# Run Alembic
# -------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()