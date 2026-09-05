"""Create the normalized ocean observations table.

Revision ID: 9a5c2d3e4f61
Revises: 7c2f0a1b9e31
Create Date: 2026-09-05

Creates the shared provider-data store used by INCOIS/Copernicus/NOAA
ingestion and ORCA retrieval.
"""

from alembic import op
import sqlalchemy as sa


revision: str = "9a5c2d3e4f61"
down_revision: str = "7c2f0a1b9e31"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("ocean_observations"):
        return

    op.create_table(
        "ocean_observations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("depth_m", sa.Float(), nullable=True),
        sa.Column("variable", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("dataset", sa.String(length=160), nullable=False),
        sa.Column("data_type", sa.String(length=32), nullable=False),
        sa.Column(
            "quality_flag",
            sa.String(length=32),
            nullable=False,
            server_default="present",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "timestamp",
            "latitude",
            "longitude",
            "variable",
            "source",
            "dataset",
            name="uq_ocean_observation_identity",
        ),
    )

    for name, columns in (
        ("ix_ocean_observations_timestamp", ["timestamp"]),
        ("ix_ocean_observations_latitude", ["latitude"]),
        ("ix_ocean_observations_longitude", ["longitude"]),
        ("ix_ocean_observations_variable", ["variable"]),
        ("ix_ocean_observations_source", ["source"]),
    ):
        op.create_index(name, "ocean_observations", columns, unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("ocean_observations"):
        return

    for name in (
        "ix_ocean_observations_source",
        "ix_ocean_observations_variable",
        "ix_ocean_observations_longitude",
        "ix_ocean_observations_latitude",
        "ix_ocean_observations_timestamp",
    ):
        op.drop_index(name, table_name="ocean_observations")

    op.drop_table("ocean_observations")
