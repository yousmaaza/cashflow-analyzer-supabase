import sys
from pathlib import Path
from loguru import logger
import json
from typing import Any, Dict


class Logger:
    """Custom logger configuration"""

    def __init__(self):
        self.configure_logger()

    def configure_logger(self):
        """Configure loguru logger"""
        # Remove default handler
        logger.remove()

        # Format for console and file
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

        # Console handler (stdout) with colors
        logger.add(
            sys.stdout,
            format=log_format,
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True
        )

        # File handler for all logs
        logger.add(
            "logs/app.log",
            format=log_format,
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

        # File handler for errors only
        logger.add(
            "logs/error.log",
            format=log_format,
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

    def info(self, message: str, **kwargs):
        """Log info message"""
        logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        logger.critical(message, **kwargs)

    def log_request(self, request_data: Dict[str, Any]):
        """Log request data in pretty format"""
        logger.info(
            "\n" + "=" * 50 + " REQUEST " + "=" * 50 +
            "\n{}".format(json.dumps(request_data, indent=2))
        )

    def log_response(self, response_data: Dict[str, Any]):
        """Log response data in pretty format"""
        logger.info(
            "\n" + "=" * 50 + " RESPONSE " + "=" * 50 +
            "\n{}".format(json.dumps(response_data, indent=2))
        )


# Global logger instance
log = Logger()