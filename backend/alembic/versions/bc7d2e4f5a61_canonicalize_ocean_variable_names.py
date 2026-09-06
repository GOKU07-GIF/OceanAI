"""Canonicalize normalized ocean variable names.

Revision ID: bc7d2e4f5a61
Revises: 9a5c2d3e4f61

This migration is retained because some existing OceanAI databases were
already stamped/applied through this revision before the migration history was
cleaned up. It is intentionally idempotent and performs the same provider-name
repair as the earlier canonicalization migration.
"""

from alembic import op


revision = "bc7d2e4f5a61"
down_revision = "9a5c2d3e4f61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE ocean_observations SET variable = 'sst_c' "
        "WHERE variable = 'sst'"
    )
    op.execute(
        "UPDATE ocean_observations SET variable = 'sst_anomaly_c' "
        "WHERE variable = 'anom'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE ocean_observations SET variable = 'sst' "
        "WHERE variable = 'sst_c'"
    )
    op.execute(
        "UPDATE ocean_observations SET variable = 'anom' "
        "WHERE variable = 'sst_anomaly_c'"
    )
