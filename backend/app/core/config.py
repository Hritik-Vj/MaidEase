from pydantic_settings import BaseSettings
from typing import List
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    APP_NAME: str = "MaidEase"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database - from Supabase
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - allow production and local URLs
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://maidease-two.vercel.app",
        "http://localhost:5173",  # For local development
        "http://localhost:3000",   # For local development
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Load CORS origins from environment if set
cors_env = os.getenv("CORS_ORIGINS", "")
if cors_env:
    # Handle both comma-separated and single values
    cors_urls = [url.strip() for url in cors_env.split(",") if url.strip()]
    settings.BACKEND_CORS_ORIGINS = cors_urls
    logger.info(f"Loaded CORS origins from environment: {cors_urls}")
else:
    logger.warning("CORS_ORIGINS environment variable not set, using defaults")

logger.info(f"Final CORS origins: {settings.BACKEND_CORS_ORIGINS}")
