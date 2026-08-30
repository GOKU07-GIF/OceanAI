from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database.base import Base


class Alert(Base):
    """
    Database model for system alerts.
    """

    __tablename__ = "alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        String(1000),
        nullable=False,
    )

    alert_type = Column(
        String(50),
        nullable=False,
        default="GENERAL",
    )

    severity = Column(
        String(20),
        nullable=False,
        default="INFO",
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    sos_id = Column(
        Integer,
        ForeignKey("sos_requests.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
    )

    sos = relationship(
        "SOS",
    )