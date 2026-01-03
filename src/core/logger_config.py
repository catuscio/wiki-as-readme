"""src.core.logger_config
Logging configuration and InterceptHandler for loguru integration.
"""

import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Redirects standard logging messages to Loguru.
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Configures logging for the application.
    Integrates Loguru with Uvicorn and Gunicorn, and suppresses noisy logs.
    """

    # 1. Remove existing handlers from Uvicorn and Gunicorn loggers
    # This prevents duplicate log outputs (one from default handler, one from Loguru).
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("gunicorn.error").handlers = []
    logging.getLogger("gunicorn.access").handlers = []

    # 2. Configure Loguru
    # Remove default handler and add a new one with a specific format.
    logger.remove()
    logger.add(
        sys.stdout,
        enqueue=True,
        backtrace=True,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    # 3. Configure Root Logger
    # Redirect all standard logging messages to the InterceptHandler.
    # Level 0 means capture everything (to be filtered later).
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # 4. Suppress noisy library logs (LiteLLM, etc.)
    # Force specific libraries to only log WARNING or higher, remove their handlers, and stop propagation.
    noisy_libraries = ["litellm", "httpcore", "httpx", "openai", "google.auth"]

    for logger_name in noisy_libraries:
        mod_logger = logging.getLogger(logger_name)
        mod_logger.setLevel(logging.WARNING)  # Only show WARNING and above
        mod_logger.handlers = []  # Remove specific handlers added by libs
        mod_logger.propagate = False  # Prevent propagation to root logger

    # 5. Bridge Uvicorn and Gunicorn logs to Loguru
    # Attach InterceptHandler to server loggers to unify log format.
    target_loggers = (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "gunicorn",
        "gunicorn.error",
        "gunicorn.access",
    )

    for logger_name in target_loggers:
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler()]
        mod_logger.propagate = False  # Prevent double logging via root logger
