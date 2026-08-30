"""create alerts table

Revision ID: 1f48f21ba3a5
Revises: 54891b6527e7
Create Date: 2026-08-22 01:10:43.883771

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "1f48f21ba3a5"

down_revision: Union[str, Sequence[str], None] = "54891b6527e7"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "alerts",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.String(length=1000),
            nullable=False,
        ),

        sa.Column(
            "alert_type",
            sa.String(length=50),
            nullable=False,
            server_default="GENERAL",
        ),

        sa.Column(
            "severity",
            sa.String(length=20),
            nullable=False,
            server_default="INFO",
        ),

        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "sos_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),

        sa.ForeignKeyConstraint(
            ["sos_id"],
            ["sos_requests.id"],
        ),
    )

    op.create_index(
        "ix_alerts_id",
        "alerts",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_alerts_id",
        table_name="alerts",
    )

    op.drop_table(
        "alerts"
    )