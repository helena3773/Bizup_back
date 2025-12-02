from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./bizup.db"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    PROJECT_NAME: str = "BIZUP API"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # 간단한 관리자 로그인용 기본 계정 정보
    # 실제 운영 환경에서는 .env 파일로 오버라이드하고, 별도의 사용자 DB/해싱
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "bizup1234"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

