import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:



    environment: str = os.getenv("ENVIRONMENT", "development")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")


    database_url: str = os.getenv("DATABASE_URL", "")


    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    def __init__(self):

        if not self.database_url:
            raise ValueError("DATABASE_URL no está configurada en .env")


@lru_cache(maxsize=1)
def get_settings() -> Settings:

    return Settings()