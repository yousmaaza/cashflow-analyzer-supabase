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
            colorize=True
        )

        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)

        # File handler for all logs
        logger.add(
            "logs/app.log",
            format=log_format,
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )

        # File handler for errors only
        logger.add(
            "logs/error.log",
            format=log_format,
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )

    def log_workflow_start(self, workflow_id: str, user_id: str):
        logger.info(
            "\n" + "🚀 "*3 +
            f"\nStarting workflow {workflow_id} for user {user_id}\n" + 
            "🚀 "*3
        )

    def log_workflow_end(self, workflow_id: str, duration: float):
        logger.info(
            "\n" + "✨ "*3 +
            f"\nWorkflow {workflow_id} completed in {duration:.2f} seconds\n" + 
            "✨ "*3
        )

    def log_workflow_error(self, workflow_id: str, error: Exception):
        logger.error(f"\n❌ Error in workflow {workflow_id}: {str(error)}")

    def log_service_call(self, service: str, action: str, workflow_id: str):
        logger.info(f"Calling {service} service to {action} for workflow {workflow_id}")

    def log_service_response(self, service: str, workflow_id: str, status: str):
        logger.info(f"Response from {service} for workflow {workflow_id}: {status}")

    def log_state_change(self, workflow_id: str, old_state: str, new_state: str):
        logger.info(f"Workflow {workflow_id} state changed: {old_state} -> {new_state}")

    def info(self, message: str):
        logger.info(message)

    def debug(self, message: str):
        logger.debug(message)

    def warning(self, message: str):
        logger.warning(message)

    def error(self, message: str):
        logger.error(message)

    def exception(self, message: str):
        logger.exception(message)

# Global logger instance
log = Logger()