import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "AI-Powered Multi-Source Opinion Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server Binding
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    
    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opinion_intel_db"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/opinion_intel_db"
    
    # Google Gemini AI Settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_ANALYZER_MODEL: str = "gemini-2.5-flash"
    GEMINI_REPORT_MODEL: str = "gemini-2.5-flash"
    
    # Reddit API Credentials
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "opinion-intel-app:v1.0"
    
    # YouTube Data API
    YOUTUBE_API_KEY: Optional[str] = None
    
    # Storage Settings
    STORAGE_DIR: str = "./storage/reports"
    MAX_UPLOAD_SIZE_MB: int = 15
    
    model_config = SettingsConfigDict(
        env_file=("backend/.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
