"""
Core configuration settings for the fraud detection platform.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FraudGuard AI"
    VERSION: str = "1.0.0"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://*.vercel.app"
    ]
    
    # Database Settings
    DATABASE_URL: str
    
    # ML Model Settings
    MODEL_PATH: str = "./ml_models"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB for audio/video files (increased from 50MB)
    
    # Security
    SECRET_KEY: str
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
