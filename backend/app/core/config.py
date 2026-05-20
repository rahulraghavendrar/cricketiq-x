from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# This finds the .env file relative to this file's location
# Goes up: config.py → core/ → app/ → backend/ → finds .env
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Gemini
    GEMINI_API_KEY: str = ""

    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "change_me"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()