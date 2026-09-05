"""create normalized ocean observations table

Revision ID: 9a5c2d3e4f61
Revises: de9d6fb29614, 7c2f0a1b9e31
Create Date: 2026-09-05

The migration merges the existing Alembic heads and adds the shared data
store used by INCOIS/Copernicus/NOAA ingestion and ORCA retrieval.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9a5c2d3e4f61"
down_revision: Union[str, Sequence[str], None] = (
    "de9d6fb29614",
    "7c2f0a1b9e31",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
        sa.Column("quality_flag", sa.String(length=32), nullable=False, server_default="present"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
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
    op.drop_index("ix_ocean_observations_source", table_name="ocean_observations")
    op.drop_index("ix_ocean_observations_variable", table_name="ocean_observations")
    op.drop_index("ix_ocean_observations_longitude", table_name="ocean_observations")
    op.drop_index("ix_ocean_observations_latitude", table_name="ocean_observations")
    op.drop_index("ix_ocean_observations_timestamp", table_name="ocean_observations")
    op.drop_table("ocean_observations")
