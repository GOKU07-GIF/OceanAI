from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ==========================================================
# Register Request
# ==========================================================

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )

    full_name: str = Field(
        min_length=3,
        max_length=100,
    )

    email: EmailStr

    phone_number: str = Field(
        min_length=10,
        max_length=15,
    )

    password: str = Field(
        min_length=8,
    )


# ==========================================================
# Login Request
# ==========================================================

class UserLogin(BaseModel):
    login: str
    password: str
    remember_me: bool = False


# ==========================================================
# Update Profile Request
# ==========================================================

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    phone_number: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=15,
    )

    language: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    profile_image: Optional[str] = None


# ==========================================================
# Change Password Request
# ==========================================================

class ChangePasswordRequest(BaseModel):
    current_password: str

    new_password: str = Field(
        min_length=8,
    )


# ==========================================================
# User Response
# ==========================================================

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    phone_number: str

    role: str

    language: str

    profile_image: Optional[str]

    is_email_verified: bool
    is_phone_verified: bool
    is_active: bool

    created_at: datetime

    class Config:
        from_attributes = True