from enum import Enum
from typing import Any, Dict, Optional


class Environment(str, Enum):
    """Enum for different deployment environments"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

    @classmethod
    def get_environment_settings(cls, env: str) -> Dict[str, Any]:
        """Get environment-specific settings based on the current environment"""
        env_settings = {
            cls.DEVELOPMENT: {
                "debug": True,
                "reload": True,
                "log_level": "DEBUG",
                "cache_ttl": 60,  # Short cache time for development
            },
            cls.TESTING: {
                "debug": True,
                "reload": False,
                "log_level": "INFO",
                "cache_ttl": 300,  # Medium cache time for testing
            },
            cls.PRODUCTION: {
                "debug": False,
                "reload": False,
                "log_level": "WARNING",
                "cache_ttl": 3600,  # Longer cache time for production
            },
        }

        return env_settings.get(env, env_settings[cls.DEVELOPMENT])
