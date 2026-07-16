from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):


    # APP
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"

    # DATABASE
    database_url: str = ""
    database_user: str = ""
    database_password: str = ""
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = ""

    # AUDIT
    audit_timeout_seconds: int = 30
    max_retries: int = 2
    playwright_timeout: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()