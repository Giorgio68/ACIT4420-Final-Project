"""
Sets up a logger with a custom format for this package
"""

import logging
import logging.config
from logging import Logger

_LOGGER_NAME = "TarjanPlanner"
_logger = logging.getLogger(_LOGGER_NAME)


_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s: %(message)s"},
        "detailed": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": f"{_LOGGER_NAME}.log",
            "maxBytes": 3_145_728,
            "backupCount": 3,
        },
    },
    "loggers": {"root": {"level": "DEBUG", "handlers": ["stdout", "file"]}},
}


def _setup_logging() -> None:
    """
    Loads the logging config for the program's execution. Note that this function is only executed
    once, during the first time this module is imported
    """
    logging.config.dictConfig(config=_config)
    _logger.debug("Logging configuration loaded successfully")


def get_logger() -> Logger:
    """
    Returns the logger to the user

    :return: The `Logger` object
    """
    return _logger


_setup_logging()
