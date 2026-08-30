from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserUpdate,
    ChangePasswordRequest,
)

from app.models.user import User

from app.services.auth_service import (
    register_user,
    login_user,
    update_profile,
    change_password,
)

from app.core.security import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =====================================================
# Register
# =====================================================

@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    return register_user(
        db=db,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        password=user.password,
    )


# =====================================================
# Login
# =====================================================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return login_user(
        db=db,
        login=form_data.username,
        password=form_data.password,
        remember_me=False,
    )


# =====================================================
# Current User
# =====================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


# =====================================================
# Update Profile
# =====================================================

@router.put(
    "/profile",
    response_model=UserResponse,
)
def update_my_profile(
    profile: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_profile(
        db=db,
        user=current_user,
        full_name=profile.full_name,
        phone_number=profile.phone_number,
        language=profile.language,
        profile_image=profile.profile_image,
    )


# =====================================================
# Change Password
# =====================================================

@router.put("/password")
def change_my_password(
    password: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return change_password(
        db=db,
        user=current_user,
        current_password=password.current_password,
        new_password=password.new_password,
    )