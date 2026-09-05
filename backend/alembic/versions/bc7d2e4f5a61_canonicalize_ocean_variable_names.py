"""Canonicalize normalized ocean variable names.

Revision ID: bc7d2e4f5a61
Revises: 9a5c2d3e4f61
"""

from alembic import op


revision = "bc7d2e4f5a61"
down_revision = "9a5c2d3e4f61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The first real INCOIS batch was ingested before the canonical-name
    # mapping was added. Repair those rows in-place so ORCA can query sst_c.
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
