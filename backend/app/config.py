from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', frozen=True)

    # required
    db_url: str
    admin_key: str = Field(..., min_length=16, max_length=128)

    # optional
    app_port: int = 8000
    host_port: int = 8000
    caddy_domain: str | None = None
    validate_urls: bool = False
    cors_origins: str = ''


settings = Settings()
