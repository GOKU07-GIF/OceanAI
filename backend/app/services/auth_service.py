from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.core.roles import UserRole
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
)

from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository


def register_user(
    db: Session,
    username: str,
    full_name: str,
    email: str,
    phone_number: str,
    password: str,
):
    """
    Register a new user.
    """

    if UserRepository.get_by_email(db, email):
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    if UserRepository.get_by_phone(db, phone_number):
        raise HTTPException(
            status_code=400,
            detail="Phone number already exists",
        )

    if UserRepository.get_by_username(db, username):
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    user = User(
        username=username,
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        hashed_password=hash_password(password),
        role=UserRole.VIEWER,
    )

    UserRepository.create_user(
        db,
        user,
    )

    logger.info(
        f"New user registered: {email}"
    )

    return user


def login_user(
    db: Session,
    login: str,
    password: str,
    remember_me: bool,
):
    """
    Login using email OR phone number.
    """

    user = UserRepository.get_by_email_or_phone(
        db,
        login,
    )

    if user is None:
        logger.warning(
            f"Failed login: {login}"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not verify_password(
        password,
        user.hashed_password,
    ):

        logger.warning(
            f"Wrong password: {login}"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        {
            "sub": user.email,
            "role": user.role.value,
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": user.email,
            "remember_me": remember_me,
        }
    )

    expires_at = (
    datetime.utcnow() + timedelta(days=30)
    if remember_me
    else datetime.utcnow() + timedelta(days=1)
)

    RefreshTokenRepository.create_refresh_token(
    db=db,
    user_id=user.id,
    token_hash=hash_token(refresh_token),
    expires_at=expires_at,
)

    user.last_login = datetime.utcnow()

    UserRepository.update_user(
        db,
        user,
    )

    logger.info(
        f"User logged in: {user.email}"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def update_profile(
    db: Session,
    user: User,
    full_name: str | None = None,
    phone_number: str | None = None,
    language: str | None = None,
    profile_image: str | None = None,
):
    """
    Update logged-in user's profile.
    """

    if phone_number is not None:

        existing = UserRepository.get_by_phone(
            db,
            phone_number,
        )

        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=400,
                detail="Phone number already exists",
            )

        user.phone_number = phone_number

    if full_name is not None:
        user.full_name = full_name

    if language is not None:
        user.language = language

    if profile_image is not None:
        user.profile_image = profile_image

    UserRepository.update_profile(
        db,
        user,
    )

    logger.info(
        f"Profile updated: {user.email}"
    )

    return user


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
):
    """
    Change password for authenticated user.
    """

    # Verify current password
    if not verify_password(
        current_password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    # Prevent same password reuse
    if verify_password(
        new_password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=400,
            detail="New password must be different",
        )

    # Hash new password
    user.hashed_password = hash_password(
        new_password,
    )

    UserRepository.update_user(
        db,
        user,
    )

    logger.info(
        f"Password changed: {user.email}"
    )

    return {
        "message": "Password changed successfully."
    }