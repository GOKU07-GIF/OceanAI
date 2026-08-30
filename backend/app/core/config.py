from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.
    All sensitive values are loaded from the .env file.
    """

    # =========================
    # Database
    # =========================
    DATABASE_URL: str

    # =========================
    # JWT Authentication
    # =========================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # =========================
    # Weather API
    # =========================
    WEATHER_API_KEY: str

    # =========================
    # Frontend
    # =========================
    FRONTEND_URL: str = "http://localhost:3000"

    # =========================
    # API
    # =========================
    API_TITLE: str = "OceanAI API"
    API_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()