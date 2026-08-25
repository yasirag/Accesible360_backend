from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "development")
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", 8000))
    api_v1_prefix: str = "/api/v1"

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost:5432/accesible360"
    )

    audit_timeout_seconds: int = 30
    max_retries: int = 2
    playwright_timeout: int = 10

    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout: int = 5
    groq_max_tokens: int = 500

    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    sendgrid_from_email: str = "noreply@nexalocal.studio"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()