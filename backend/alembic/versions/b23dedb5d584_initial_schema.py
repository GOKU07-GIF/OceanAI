"""initial_schema

Revision ID: b23dedb5d584
Revises:
Create Date: 2026-08-02 18:40:44.072591
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = "b23dedb5d584"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial OceanAI database schema."""

    # -------------------------------------------------------------------------
    # Users Table
    # -------------------------------------------------------------------------
    op.create_table(
        "users",

        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "username",
            sa.String(50),
            nullable=False,
        ),

        sa.Column(
            "full_name",
            sa.String(100),
            nullable=False,
        ),

        sa.Column(
            "email",
            sa.String(255),
            nullable=False,
        ),

        sa.Column(
            "phone_number",
            sa.String(15),
            nullable=False,
        ),

        sa.Column(
            "hashed_password",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "role",
            sa.Enum(
                "admin",
                "researcher",
                "viewer",
                name="userrole",
            ),
            nullable=False,
            server_default="viewer",
        ),

        sa.Column(
            "language",
            sa.String(20),
            nullable=False,
            server_default="English",
        ),

        sa.Column(
            "profile_image",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "is_phone_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "last_login",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # -------------------------------------------------------------------------
    # Users Indexes
    # -------------------------------------------------------------------------
    op.create_index(
        op.f("ix_users_id"),
        "users",
        ["id"],
    )

    op.create_index(
        op.f("ix_users_username"),
        "users",
        ["username"],
        unique=True,
    )

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    op.create_index(
        op.f("ix_users_phone_number"),
        "users",
        ["phone_number"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # Refresh Tokens Table
    # -------------------------------------------------------------------------
    op.create_table(
        "refresh_tokens",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "token_hash",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "is_revoked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )

    # -------------------------------------------------------------------------
    # Refresh Token Indexes
    # -------------------------------------------------------------------------
    op.create_index(
        op.f("ix_refresh_tokens_id"),
        "refresh_tokens",
        ["id"],
    )

    op.create_index(
        op.f("ix_refresh_tokens_token_hash"),
        "refresh_tokens",
        ["token_hash"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # Ocean Data Foreign Key
    # -------------------------------------------------------------------------
    op.create_foreign_key(
        "fk_ocean_data_owner_id",
        "ocean_data",
        "users",
        ["owner_id"],
        ["id"],
    )


def downgrade() -> None:
    """Drop initial OceanAI schema."""

    op.drop_constraint(
        "fk_ocean_data_owner_id",
        "ocean_data",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_refresh_tokens_token_hash"),
        table_name="refresh_tokens",
    )

    op.drop_index(
        op.f("ix_refresh_tokens_id"),
        table_name="refresh_tokens",
    )

    op.drop_table("refresh_tokens")

    op.drop_index(
        op.f("ix_users_phone_number"),
        table_name="users",
    )

    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )

    op.drop_index(
        op.f("ix_users_username"),
        table_name="users",
    )

    op.drop_index(
        op.f("ix_users_id"),
        table_name="users",
    )

    op.drop_table("users")