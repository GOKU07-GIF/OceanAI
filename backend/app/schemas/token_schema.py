from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    """
    Request body for refreshing an access token.
    """

    refresh_token: str = Field(
        ...,
        description="JWT Refresh Token",
        min_length=20,
    )


class TokenResponse(BaseModel):
    """
    Response returned after login or token refresh.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    """
    Request body for logout.
    """

    refresh_token: str = Field(
        ...,
        description="JWT Refresh Token",
        min_length=20,
    )


class MessageResponse(BaseModel):
    """
    Generic success response.
    """

    message: str