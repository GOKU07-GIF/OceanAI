"""create normalized ocean observations

Revision ID: c1a2b3d4e5f6
Revises: 7c2f0a1b9e31

Creates the shared provider-data table used by the OceanAI ingestion layer and
ORCA. Provider observations are intentionally independent of application users.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1a2b3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "7c2f0a1b9e31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the normalized ocean observation store."""
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
        sa.Column("quality_flag", sa.String(length=32), nullable=False, server_default="present"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
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

    op.create_index(
        "ix_ocean_observations_timestamp",
        "ocean_observations",
        ["timestamp"],
        unique=False,
    )
    op.create_index(
        "ix_ocean_observations_latitude",
        "ocean_observations",
        ["latitude"],
        unique=False,
    )
    op.create_index(
        "ix_ocean_observations_longitude",
        "ocean_observations",
        ["longitude"],
        unique=False,
    )
    op.create_index(
        "ix_ocean_observations_variable",
        "ocean_observations",
        ["variable"],
        unique=False,
    )
    op.create_index(
        "ix_ocean_observations_source",
        "ocean_observations",
        ["source"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the normalized ocean observation store."""
    op.drop_index("ix_ocean_observations_source", table_name="ocean_observations")
    op.drop_index("ix_ocean_observations_variable", table_name="ocean_observations")
    op.drop_index("ix_ocean_observations_longitude", table_name="ocean_observations")
    op.drop_index("ix_ocean_observations_latitude", table_name="ocean_observations")
    op.drop_index("ix_ocean_observations_timestamp", table_name="ocean_observations")
    op.drop_table("ocean_observations")
