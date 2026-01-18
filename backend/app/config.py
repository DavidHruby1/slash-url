from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', frozen=True)

    # required
    db_url: str
    admin_key: str

    # optional
    app_port: int = 8000
    host_port: int = 8000
    caddy_domain: str | None = None
    validate_urls: bool = False
    cors_origins: str = ''

    @classmethod
    @field_validator('admin_key')
    def validate_admin_key(cls, value: str) -> str:
        if not value or len(value) < 16:
            raise ValueError('Admin key does not exist or is too short.')
        return value


settings = Settings()
