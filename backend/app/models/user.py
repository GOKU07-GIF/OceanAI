from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Enum as SQLAlchemyEnum,
)

from sqlalchemy.orm import relationship

from app.database.base import Base
from app.core.roles import UserRole


class User(Base):
    """
    User Model
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    phone_number = Column(
        String(15),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password = Column(
        String,
        nullable=False,
    )

    role = Column(
        SQLAlchemyEnum(
            UserRole,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=True,
        ),
        nullable=False,
        default=UserRole.VIEWER,
        server_default=UserRole.VIEWER.value,
    )

    language = Column(
        String(20),
        default="English",
        nullable=False,
    )

    profile_image = Column(
        String,
        nullable=True,
    )

    is_email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_phone_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    last_login = Column(
        DateTime,
        nullable=True,
    )

    ocean_data = relationship(
        "OceanData",
        back_populates="owner",
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<User(username='{self.username}', "
            f"email='{self.email}')>"
        )