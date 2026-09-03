"""Restore sensor tables removed by the SOS migration.

Revision ID: 7c2f0a1b9e31
Revises: 1f48f21ba3a5
"""

from alembic import op
import sqlalchemy as sa


revision = "7c2f0a1b9e31"
down_revision = "1f48f21ba3a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("sensor_devices"):
        op.create_table(
            "sensor_devices",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("device_id", sa.String(length=100), nullable=False),
            sa.Column("device_name", sa.String(length=100), nullable=False),
            sa.Column("device_type", sa.String(length=50), nullable=False),
            sa.Column("latitude", sa.Float(), nullable=False),
            sa.Column("longitude", sa.Float(), nullable=False),
            sa.Column("firmware_version", sa.String(length=30), nullable=True),
            sa.Column("battery_level", sa.Float(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.UniqueConstraint("device_id"),
        )
        op.create_index("ix_sensor_devices_id", "sensor_devices", ["id"], unique=False)
        op.create_index("ix_sensor_devices_device_id", "sensor_devices", ["device_id"], unique=True)

    inspector = sa.inspect(bind)
    if not inspector.has_table("sensor_readings"):
        op.create_table(
            "sensor_readings",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("sensor_device_id", sa.Integer(), nullable=False),
            sa.Column("temperature", sa.Float(), nullable=False),
            sa.Column("ph", sa.Float(), nullable=False),
            sa.Column("salinity", sa.Float(), nullable=False),
            sa.Column("oxygen", sa.Float(), nullable=False),
            sa.Column("turbidity", sa.Float(), nullable=False),
            sa.Column("water_quality", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["sensor_device_id"], ["sensor_devices.id"]),
        )
        op.create_index("ix_sensor_readings_id", "sensor_readings", ["id"], unique=False)


def downgrade() -> None:
    # Intentionally preserve repaired sensor tables and their data.
    # Removing them during downgrade would be destructive.
    pass
