from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any, Union
from app.core.environment import Environment
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ESDA Web Mapping API"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Frontend URL
    
    # Environment Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
    ENV_SETTINGS: Dict[str, Any] = Environment.get_environment_settings(ENVIRONMENT)
    
    # Database Settings
    DATABASE_URL: Optional[str] = None  # Add if using a database
    
    # Redis Cache Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", ENV_SETTINGS.get("cache_ttl", 3600)))
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", ENV_SETTINGS.get("log_level", "INFO"))
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "logs/app.log")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()