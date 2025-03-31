import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class EnvironmentType(str, Enum):
    """Enum for different deployment environments"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseSettings(BaseModel):
    """Database configuration settings"""

    url: Optional[str] = None
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False
    echo_pool: bool = False
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    connect_timeout: int = 30


class CacheSettings(BaseModel):
    """Cache configuration settings"""

    ttl: int = 3600  # Default TTL in seconds
    namespace: str = "esda-cache"
    key_prefix: str = ""
    serializer: str = "json"  # Options: json, pickle, msgpack
    compression: bool = False


class LoggingSettings(BaseModel):
    """Logging configuration settings"""

    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: str = "json"  # json, text
    file: Optional[str] = None
    rotation: str = "10 MB"  # Size-based rotation
    retention: str = "1 month"  # Time-based retention
    compression: str = "gz"  # Compression format for rotated logs
    backtrace: bool = True  # Include exception backtraces
    diagnose: bool = True  # Include diagnostic info for exceptions
    structured: bool = True  # Use structured logging
    enrich: List[str] = ["process", "thread", "module"]  # Enrich log records


class SecuritySettings(BaseModel):
    """Security configuration settings"""

    jwt_secret_key: str = ""  # Should be set from environment
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_bcrypt_rounds: int = 12
    cors_origins: List[str] = ["http://localhost:3000"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    rate_limit_requests: int = 100  # Requests per minute
    rate_limit_period: int = 60  # Period in seconds


class APISettings(BaseModel):
    """API configuration settings"""

    prefix: str = "/api/v1"
    title: str = "ESDA Web Mapping API"
    description: str = "API for serving geospatial data and analysis results."
    version: str = "0.1.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    root_path: str = ""
    debug: bool = False
    reload: bool = False


class EnvironmentConfig:
    """Environment configuration manager"""

    @classmethod
    def get_environment_type(cls) -> EnvironmentType:
        """Get the current environment type from environment variables"""
        env = os.getenv("ENVIRONMENT", EnvironmentType.DEVELOPMENT)
        try:
            return EnvironmentType(env)
        except ValueError:
            return EnvironmentType.DEVELOPMENT

    @classmethod
    def load_environment_file(cls, env_type: EnvironmentType) -> Dict[str, Any]:
        """Load environment-specific configuration from a file"""
        config_dir = os.path.join(os.path.dirname(__file__), "../..", "config")
        config_file = os.path.join(config_dir, f"{env_type}.json")

        # Default configuration
        default_config = {
            EnvironmentType.DEVELOPMENT: {
                "debug": True,
                "reload": True,
                "log_level": "DEBUG",
                "cache_ttl": 60,  # Short cache time for development
            },
            EnvironmentType.TESTING: {
                "debug": True,
                "reload": False,
                "log_level": "INFO",
                "cache_ttl": 300,  # Medium cache time for testing
            },
            EnvironmentType.STAGING: {
                "debug": False,
                "reload": False,
                "log_level": "INFO",
                "cache_ttl": 1800,  # Medium-long cache time for staging
            },
            EnvironmentType.PRODUCTION: {
                "debug": False,
                "reload": False,
                "log_level": "WARNING",
                "cache_ttl": 3600,  # Longer cache time for production
            },
        }

        # Try to load from file if it exists
        try:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    file_config = json.load(f)
                    # Merge with default config
                    return {**default_config.get(env_type, {}), **file_config}
        except Exception as e:
            print(f"Error loading config file {config_file}: {str(e)}")

        # Return default config if file doesn't exist or has errors
        return default_config.get(env_type, default_config[EnvironmentType.DEVELOPMENT])

    @classmethod
    def get_database_settings(cls, env_type: EnvironmentType) -> DatabaseSettings:
        """Get database settings for the current environment"""
        config = cls.load_environment_file(env_type)
        db_config = config.get("database", {})

        # Override with environment variables if set
        if os.getenv("DATABASE_URL"):
            db_config["url"] = os.getenv("DATABASE_URL")

        return DatabaseSettings(**db_config)

    @classmethod
    def get_cache_settings(cls, env_type: EnvironmentType) -> CacheSettings:
        """Get cache settings for the current environment"""
        config = cls.load_environment_file(env_type)
        cache_config = config.get("cache", {})

        # Override with environment variables if set
        if os.getenv("CACHE_TTL"):
            cache_config["ttl"] = int(os.getenv("CACHE_TTL"))

        return CacheSettings(**cache_config)

    @classmethod
    def get_logging_settings(cls, env_type: EnvironmentType) -> LoggingSettings:
        """Get logging settings for the current environment"""
        config = cls.load_environment_file(env_type)
        log_config = config.get("logging", {})

        # Override with environment variables if set
        if os.getenv("LOG_LEVEL"):
            log_config["level"] = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FORMAT"):
            log_config["format"] = os.getenv("LOG_FORMAT")
        if os.getenv("LOG_FILE"):
            log_config["file"] = os.getenv("LOG_FILE")

        return LoggingSettings(**log_config)

    @classmethod
    def get_security_settings(cls, env_type: EnvironmentType) -> SecuritySettings:
        """Get security settings for the current environment"""
        config = cls.load_environment_file(env_type)
        security_config = config.get("security", {})

        # Override with environment variables if set
        if os.getenv("JWT_SECRET_KEY"):
            security_config["jwt_secret_key"] = os.getenv("JWT_SECRET_KEY")
        if os.getenv("JWT_ALGORITHM"):
            security_config["jwt_algorithm"] = os.getenv("JWT_ALGORITHM")
        if os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"):
            security_config["access_token_expire_minutes"] = int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
            )
        if os.getenv("CORS_ORIGINS"):
            try:
                security_config["cors_origins"] = json.loads(os.getenv("CORS_ORIGINS"))
            except:
                # Fallback to comma-separated list
                security_config["cors_origins"] = os.getenv("CORS_ORIGINS").split(",")

        return SecuritySettings(**security_config)

    @classmethod
    def get_api_settings(cls, env_type: EnvironmentType) -> APISettings:
        """Get API settings for the current environment"""
        config = cls.load_environment_file(env_type)
        api_config = config.get("api", {})

        # Override with environment variables if set
        if os.getenv("API_PREFIX"):
            api_config["prefix"] = os.getenv("API_PREFIX")
        if os.getenv("API_TITLE"):
            api_config["title"] = os.getenv("API_TITLE")
        if os.getenv("API_VERSION"):
            api_config["version"] = os.getenv("API_VERSION")

        return APISettings(**api_config)

    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all settings for the current environment"""
        env_type = cls.get_environment_type()

        return {
            "environment": env_type,
            "database": cls.get_database_settings(env_type).dict(),
            "cache": cls.get_cache_settings(env_type).dict(),
            "logging": cls.get_logging_settings(env_type).dict(),
            "security": cls.get_security_settings(env_type).dict(),
            "api": cls.get_api_settings(env_type).dict(),
        }


# Create a directory for environment-specific config files if it doesn't exist
config_dir = os.path.join(os.path.dirname(__file__), "../..", "config")
os.makedirs(config_dir, exist_ok=True)

# Export environment type and settings
environment_type = EnvironmentConfig.get_environment_type()
environment_settings = EnvironmentConfig.get_all_settings()
