from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/bizup.db"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    PROJECT_NAME: str = "BIZUP API"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "bizup1234"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

