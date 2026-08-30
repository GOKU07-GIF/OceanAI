"""add is_active to ocean data

Revision ID: de9d6fb29614
Revises: 187d4dd02f7e
Create Date: 2026-08-08 17:29:05.946311

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "de9d6fb29614"
down_revision: Union[str, Sequence[str], None] = "187d4dd02f7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "ocean_data",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "ocean_data",
        "is_active",
    )