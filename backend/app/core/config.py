from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any, Union
from app.core.environment import Environment
import os
from pathlib import Path

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ESDA Web Mapping API"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Environment Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
    ENV_SETTINGS: Dict[str, Any] = Environment.get_environment_settings(ENVIRONMENT)
    
    # Base Directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    # Database Settings
    DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_POOL_PRE_PING: bool = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
    
    # Redis Cache Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", ENV_SETTINGS.get("cache_ttl", "3600")))
    CACHE_NAMESPACE: str = os.getenv("CACHE_NAMESPACE", f"esda-cache-{ENVIRONMENT}")
    CACHE_KEY_PREFIX: str = os.getenv("CACHE_KEY_PREFIX", f"{ENVIRONMENT}:")
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", ENV_SETTINGS.get("log_level", "INFO"))
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))
    LOG_ROTATION: str = os.getenv("LOG_ROTATION", "100 MB")
    LOG_RETENTION: str = os.getenv("LOG_RETENTION", "1 month")
    LOG_COMPRESSION: bool = os.getenv("LOG_COMPRESSION", "true").lower() == "true"
    
    # Security Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", ENV_SETTINGS.get("jwt_secret_key", "dev-secret-key"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    PASSWORD_BCRYPT_ROUNDS: int = int(os.getenv("PASSWORD_BCRYPT_ROUNDS", "12"))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    # Geospatial Settings
    DEFAULT_SRID: int = int(os.getenv("DEFAULT_SRID", "4326"))
    MAX_GEOMETRY_POINTS: int = int(os.getenv("MAX_GEOMETRY_POINTS", "10000"))
    GEOMETRY_SIMPLIFICATION_TOLERANCE: float = float(os.getenv("GEOMETRY_SIMPLIFICATION_TOLERANCE", "0.0001"))
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_database_url(self) -> str:
        """Get the database URL with proper formatting."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'esda_db')}"

    def get_logging_config(self) -> Dict[str, Any]:
        """Get the logging configuration dictionary."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": self.LOG_LEVEL
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": self.LOG_FILE,
                    "maxBytes": self._parse_size(self.LOG_ROTATION),
                    "backupCount": 5,
                    "formatter": "json",
                    "level": self.LOG_LEVEL
                }
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console", "file"]
            }
        }

    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Convert size string (e.g., '100 MB') to bytes."""
        units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        number = float(size_str.split()[0])
        unit = size_str.split()[1].upper()
        return int(number * units[unit])

settings = Settings()