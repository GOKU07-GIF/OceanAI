from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Repository responsible only for database operations
    related to the User model.
    """

    # ==========================================================
    # Get Users
    # ==========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def get_by_phone(
        db: Session,
        phone_number: str,
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.phone_number == phone_number)
            .first()
        )

    @staticmethod
    def get_by_username(
        db: Session,
        username: str,
    ) -> User | None:

        return (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

    @staticmethod
    def get_by_email_or_phone(
        db: Session,
        login: str,
    ) -> User | None:
        """
        Login using email or phone number.
        """

        return (
            db.query(User)
            .filter(
                or_(
                    User.email == login,
                    User.phone_number == login,
                )
            )
            .first()
        )

    # ==========================================================
    # Create
    # ==========================================================

    @staticmethod
    def create_user(
        db: Session,
        user: User,
    ) -> User:

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # ==========================================================
    # Update
    # ==========================================================

    @staticmethod
    def update_user(
        db: Session,
        user: User,
    ) -> User:

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_last_login(
        db: Session,
        user: User,
    ) -> User:

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_profile(
        db: Session,
        user: User,
    ) -> User:

        db.commit()
        db.refresh(user)

        return user

    # ==========================================================
    # Delete
    # ==========================================================

    @staticmethod
    def delete_user(
        db: Session,
        user: User,
    ) -> None:

        db.delete(user)
        db.commit()