import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from loguru import logger as loguru_logger
from pythonjsonlogger import jsonlogger

from app.core.config import settings


# Ensure log directory exists
def setup_log_directory():
    if settings.LOG_FILE:
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and log_dir != "":
            Path(log_dir).mkdir(parents=True, exist_ok=True)


# Configure JSON formatter for structured logging
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["environment"] = settings.ENVIRONMENT
        log_record["service"] = settings.PROJECT_NAME
        log_record["timestamp"] = record.created
        log_record["level"] = record.levelname


# Setup standard Python logging
def setup_logging():
    setup_log_directory()

    # Get the root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    root_logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Format based on settings
    if settings.LOG_FORMAT.lower() == "json":
        formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler if LOG_FILE is specified
    if settings.LOG_FILE:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE, maxBytes=10485760, backupCount=5  # 10MB
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Configure loguru to use the same handlers
    loguru_logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": settings.LOG_LEVEL.upper(), "format": formatter._fmt},
            (
                {
                    "sink": settings.LOG_FILE,
                    "level": settings.LOG_LEVEL.upper(),
                    "format": formatter._fmt,
                }
                if settings.LOG_FILE
                else None
            ),
        ]
    )

    return root_logger


# Get a logger for a specific module
def get_logger(name):
    return logging.getLogger(name)
