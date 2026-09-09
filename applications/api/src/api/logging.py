import logging


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s <%(name)s>: %(message)s",
    )
