"""Canonicalize provider variable names in the normalized ocean store.

Revision ID: b84c0e7d2a91
Revises: 9a5c2d3e4f61
"""

from alembic import op
import sqlalchemy as sa

revision = "b84c0e7d2a91"
down_revision = "9a5c2d3e4f61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # Provider-native names already stored by earlier ingestion runs are
    # converted once to the names ORCA uses internally.
    bind.execute(
        sa.text(
            "UPDATE ocean_observations "
            "SET variable = 'sst_c' "
            "WHERE variable = 'sst'"
        )
    )
    bind.execute(
        sa.text(
            "UPDATE ocean_observations "
            "SET variable = 'sst_anomaly_c' "
            "WHERE variable = 'anom'"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE ocean_observations "
            "SET variable = 'sst' "
            "WHERE variable = 'sst_c'"
        )
    )
    bind.execute(
        sa.text(
            "UPDATE ocean_observations "
            "SET variable = 'anom' "
            "WHERE variable = 'sst_anomaly_c'"
        )
    )
