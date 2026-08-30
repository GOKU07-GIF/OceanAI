from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base


class RefreshToken(Base):
    """
    SQLAlchemy model for tracking Refresh Tokens.
    We store the HASH of the token, not the raw token, for security.
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    
    # The SHA-256 hash of the raw JWT refresh token
    token_hash = Column(String, unique=True, index=True, nullable=False)
    
    # Link to the user who owns this token
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # When the token expires
    expires_at = Column(DateTime, nullable=False)
    
    # Flag to handle Logout (Revocation)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to User
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"