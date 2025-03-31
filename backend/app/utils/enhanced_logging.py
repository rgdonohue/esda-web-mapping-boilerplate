import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union

from loguru import logger as loguru_logger
from pythonjsonlogger import jsonlogger

from app.core.environment_config import EnvironmentConfig, environment_type


class EnhancedLogger:
    """Enhanced logging system with support for structured logging, rotation, and multiple outputs"""

    def __init__(self):
        self.log_settings = EnvironmentConfig.get_logging_settings(environment_type)
        self.setup_log_directory()
        self.root_logger = self.setup_logging()

    def setup_log_directory(self):
        """Ensure log directory exists"""
        if self.log_settings.file:
            log_dir = os.path.dirname(self.log_settings.file)
            if log_dir and log_dir != "":
                Path(log_dir).mkdir(parents=True, exist_ok=True)

    def get_formatter(self):
        """Get the appropriate formatter based on settings"""
        if self.log_settings.format.lower() == "json":
            return CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
        else:
            return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def setup_logging(self):
        """Setup standard Python logging with enhanced features"""
        # Get the root logger
        root_logger = logging.getLogger()

        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Set log level
        log_level = getattr(logging, self.log_settings.level.upper())
        root_logger.setLevel(log_level)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Get formatter
        formatter = self.get_formatter()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler if LOG_FILE is specified
        if self.log_settings.file:
            # Parse rotation settings
            if self.log_settings.rotation:
                if self.log_settings.rotation.endswith("MB"):
                    # Size-based rotation
                    size_mb = int(self.log_settings.rotation.split()[0])
                    file_handler = RotatingFileHandler(
                        self.log_settings.file, maxBytes=size_mb * 1024 * 1024, backupCount=10
                    )
                else:
                    # Time-based rotation
                    file_handler = TimedRotatingFileHandler(
                        self.log_settings.file, when="midnight", interval=1, backupCount=30
                    )
            else:
                # Default to rotating file handler
                file_handler = RotatingFileHandler(
                    self.log_settings.file, maxBytes=10485760, backupCount=5  # 10MB
                )

            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Configure loguru to use the same handlers
        loguru_config = {
            "handlers": [
                {
                    "sink": sys.stdout,
                    "level": self.log_settings.level.upper(),
                    "format": formatter._fmt,
                },
            ]
        }

        if self.log_settings.file:
            loguru_config["handlers"].append(
                {
                    "sink": self.log_settings.file,
                    "level": self.log_settings.level.upper(),
                    "format": formatter._fmt,
                }
            )

        loguru_logger.configure(**loguru_config)

        return root_logger

    def get_logger(self, name):
        """Get a logger for a specific module"""
        return logging.getLogger(name)


# Custom JSON formatter for structured logging
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["environment"] = environment_type
        log_record["timestamp"] = record.created
        log_record["level"] = record.levelname

        # Add extra fields for structured logging
        if hasattr(record, "props"):
            for key, value in record.props.items():
                log_record[key] = value


# Create a singleton instance
logger_instance = EnhancedLogger()


# Export the get_logger function
def get_logger(name):
    """Get a logger for a specific module"""
    return logger_instance.get_logger(name)


# Utility function for structured logging
def log_with_context(logger, level, message, **context):
    """Log a message with additional context data"""
    extra = {"props": context}
    logger.log(level, message, extra=extra)


# Export convenience functions
def debug(logger, message, **context):
    log_with_context(logger, logging.DEBUG, message, **context)


def info(logger, message, **context):
    log_with_context(logger, logging.INFO, message, **context)


def warning(logger, message, **context):
    log_with_context(logger, logging.WARNING, message, **context)


def error(logger, message, **context):
    log_with_context(logger, logging.ERROR, message, **context)


def critical(logger, message, **context):
    log_with_context(logger, logging.CRITICAL, message, **context)


# Exception logging with context
def exception(logger, message, exc_info=True, **context):
    """Log an exception with additional context data"""
    extra = {"props": context}
    logger.exception(message, exc_info=exc_info, extra=extra)
