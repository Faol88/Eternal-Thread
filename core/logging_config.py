"""
core.logging_config
~~~~~~~~~~~~~~~~~~~
Logging configuration for the Living Memory Core library.
Provides a unified logger without polluting parent application loggers.
"""

import logging

LOGGER_NAME = "eternal_memory_core"
logger = logging.getLogger(LOGGER_NAME)

# Set NullHandler by default so library doesn't output unless configured by user
if not logger.handlers:
    logger.addHandler(logging.NullHandler())


def setup_default_logging(level: int = logging.INFO) -> None:
    """Configures a clean console logger for standalone scripts or debugging."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
