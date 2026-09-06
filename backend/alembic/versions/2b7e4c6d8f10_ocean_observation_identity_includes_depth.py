"""Include depth in normalized ocean observation identity.

Revision ID: 2b7e4c6d8f10
Revises: b84c0e7d2a91 and bc7d2e4f5a61
Create Date: 2026-09-06

Profile products such as ARGO can contain multiple depth levels at the same
(timestamp, latitude, longitude, variable). The original unique constraint did
not include depth_m, so most profile rows were incorrectly skipped as
conflicts. Surface/gridded observations with a missing depth are normalized to
0 m before the new constraint is created so reruns remain idempotent.

This migration intentionally merges the two historical canonicalization
revisions because some existing databases were already stamped through either
one. Both predecessor migrations are idempotent provider-name repairs.
"""

from alembic import op
import sqlalchemy as sa


revision: str = "2b7e4c6d8f10"
down_revision = ("b84c0e7d2a91", "bc7d2e4f5a61")
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("ocean_observations"):
        return

    columns = {column["name"] for column in inspector.get_columns("ocean_observations")}
    if "depth_m" not in columns:
        op.add_column("ocean_observations", sa.Column("depth_m", sa.Float(), nullable=True))

    # Surface observations historically used NULL depth. Normalize those to
    # an explicit 0 m so the depth-inclusive uniqueness rule is effective for
    # non-profile datasets as well.
    op.execute(
        sa.text(
            "UPDATE ocean_observations "
            "SET depth_m = 0.0 "
            "WHERE depth_m IS NULL"
        )
    )

    constraints = {constraint["name"] for constraint in inspector.get_unique_constraints("ocean_observations")}
    if "uq_ocean_observation_identity" in constraints:
        op.drop_constraint(
            "uq_ocean_observation_identity",
            "ocean_observations",
            type_="unique",
        )

    op.create_unique_constraint(
        "uq_ocean_observation_identity",
        "ocean_observations",
        [
            "timestamp",
            "latitude",
            "longitude",
            "depth_m",
            "variable",
            "source",
            "dataset",
        ],
    )

    indexes = {index["name"] for index in inspector.get_indexes("ocean_observations")}
    if "ix_ocean_observations_depth_m" not in indexes:
        op.create_index(
            "ix_ocean_observations_depth_m",
            "ocean_observations",
            ["depth_m"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("ocean_observations"):
        return

    indexes = {index["name"] for index in inspector.get_indexes("ocean_observations")}
    if "ix_ocean_observations_depth_m" in indexes:
        op.drop_index("ix_ocean_observations_depth_m", table_name="ocean_observations")

    constraints = {constraint["name"] for constraint in inspector.get_unique_constraints("ocean_observations")}
    if "uq_ocean_observation_identity" in constraints:
        op.drop_constraint(
            "uq_ocean_observation_identity",
            "ocean_observations",
            type_="unique",
        )

    op.create_unique_constraint(
        "uq_ocean_observation_identity",
        "ocean_observations",
        [
            "timestamp",
            "latitude",
            "longitude",
            "variable",
            "source",
            "dataset",
        ],
    )
