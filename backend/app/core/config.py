from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Development-only defaults that must never reach a non-development environment.
INSECURE_JWT_SECRETS = {"", "change-me", "change-me-to-a-long-random-string"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"

    database_url: str = "postgresql+psycopg://capacitador:capacitador@localhost:5432/capacitador_it"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    google_client_id: str = ""

    cors_origins: str = "http://localhost:5173"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_public_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "capacitador-it"
    s3_region: str = "us-east-1"
    s3_use_ssl: bool = False

    max_upload_size_mb: int = 200

    superadmin_email: str = ""
    superadmin_name: str = "Super Administrator"

    @model_validator(mode="after")
    def _reject_insecure_secrets_outside_development(self) -> "Settings":
        # A known JWT secret lets anyone mint valid tokens (full auth bypass).
        if self.environment != "development" and self.jwt_secret in INSECURE_JWT_SECRETS:
            raise ValueError("JWT_SECRET must be set to a long random value when ENVIRONMENT is not 'development'.")
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
