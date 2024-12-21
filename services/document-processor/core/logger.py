import sys
import json
from pathlib import Path
from loguru import logger

class CustomLogger:
    def __init__(self):
        self.configure_logger()

    def configure_logger(self):
        # Supprimer le handler par défaut
        logger.remove()

        # Format personnalisé pour les logs
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

        # Handler pour la console avec des couleurs
        logger.add(
            sys.stdout,
            format=log_format,
            level="DEBUG",
            colorize=True,
        )

        # Créer le dossier logs s'il n'existe pas
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Handler pour le fichier avec rotation
        logger.add(
            "logs/app.log",
            format=log_format,
            level="INFO",
            rotation="10 MB",
            compression="zip",
            retention="30 days",
            backtrace=False,
            diagnose=False,
            enqueue=False,
        )

        # Handler pour les erreurs séparé
        logger.add(
            "logs/error.log",
            format=log_format,
            level="ERROR",
            rotation="10 MB",
            compression="zip",
            retention="30 days",
            backtrace=False,
            diagnose=False,
            enqueue=False,
        )

    def log_request(self, request_data):
        """Log les détails d'une requête avec un format joli"""
        logger.info(
            "\n" + "="*50 + " REQUEST " + "="*50 + 
            "\n{}".format(
                json.dumps(request_data, indent=2)
            )
        )

    def log_result(self, result_data):
        """Log les résultats avec un format joli"""
        logger.info(
            "\n" + "="*50 + " RESULT " + "="*50 + 
            "\n{}".format(
                json.dumps(result_data, indent=2)
            )
        )

    def log_process_start(self, filename: str):
        logger.info(
            "\n" + "🚀 "*3 +
            f"\nStarting processing of: {filename}\n" + 
            "🚀 "*20
        )

    def log_process_end(self, filename: str, duration: float):
        logger.info(
            "\n" + "✨ "*3 +
            f"\nFinished processing {filename} in {duration:.2f} seconds\n" + 
            "✨ "*20
        )

    def log_error(self, error: Exception, context: str = ""):
        logger.exception(f"\n❌ Error : {str(error)}")

    def info(self, message):
        logger.info(message)

    def debug(self, message):
        logger.debug(message)

    def warning(self, message):
        logger.warning(message)

    def error(self, message):
        logger.error(message)

    def exception(self, message):
        logger.exception(message)

# Instance globale du logger
log = CustomLogger()
