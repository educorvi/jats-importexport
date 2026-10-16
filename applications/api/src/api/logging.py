import logging

from api.config import APIConfig


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=APIConfig.LOG_LEVEL,
        format="[%(levelname)s] %(asctime)s <%(name)s>: %(message)s",
    )
