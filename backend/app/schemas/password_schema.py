from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    """
    Request schema for forgot password.
    """

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Request schema for resetting password.
    """

    token: str = Field(
        min_length=20,
        description="Password reset token",
    )

    new_password: str = Field(
        min_length=8,
        max_length=100,
        description="New password",
    )