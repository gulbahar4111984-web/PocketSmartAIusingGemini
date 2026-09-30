from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    environment: str = "development"

    secret_key: str = "change-this-secret-key"

    database_url: str = "sqlite:///./pocketsmart.db"

    gemini_api_key: str | None = None

    # Change this in .env if your Gemini account uses another model.
    gemini_model: str ="gemini-3.8-flash"

    access_token_expire_minutes: int = 1440

    max_upload_mb: int = 5

    allowed_origins: str = (
        "http://127.0.0.1:8000,"
        "http://localhost:8000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()