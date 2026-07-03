from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    aws_region: str = "us-east-1"
    aws_endpoint_url: str | None = "http://localhost:4566"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"

    cognito_user_pool_id: str
    cognito_client_id: str
    cognito_client_secret: str | None = None
    cognito_domain: str

    # google_oauth_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    # google_oauth_scopes: str = "openid email profile"

    ses_sender_email: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
