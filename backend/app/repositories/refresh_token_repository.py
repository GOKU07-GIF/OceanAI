from datetime import datetime
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """
    Repository for handling Refresh Token database operations.
    """

    @staticmethod
    def create_refresh_token(
        db: Session,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """
        Creates and saves a new hashed refresh token to the database.
        """
        new_refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
            created_at=datetime.utcnow(),
        )
        
        db.add(new_refresh_token)
        db.commit()
        db.refresh(new_refresh_token)
        
        return new_refresh_token

    @staticmethod
    def get_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
        """
        Retrieves a refresh token record by its hash.
        Returns None if not found.
        """
        return db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False
        ).first()

    @staticmethod
    def revoke_token(db: Session, token_hash: str) -> bool:
        """
        Marks a refresh token as revoked (used for Logout).
        Returns True if a token was found and revoked, False otherwise.
        """
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        
        if token_record:
            token_record.is_revoked = True
            db.commit()
            return True
            
        return False

    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int) -> None:
        """
        Revokes all active refresh tokens for a specific user.
        Useful for "Logout from all devices" functionality.
        """
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        db.commit()