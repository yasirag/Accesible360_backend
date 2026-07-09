from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./audits.db"

    groq_api_key: str = ""


class Config:
    env_file = ".env"
    case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()