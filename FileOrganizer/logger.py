"""
Sets up a logger with a custom format for this package
"""

import json
import logging
import logging.config
from logging import Logger
from pathlib import Path


_LOGGER_NAME = "FileOrganizer"
_logger = logging.getLogger(_LOGGER_NAME)
_config_path = Path(".") / "config" / "log_config.json"


def _setup_logging() -> None:
    """
    Loads the logging config for the program's execution. Note that this function is only executed
    once, during the first time this module is imported
    """
    with open(_config_path, "rb") as _file_config:
        _config = json.load(_file_config)

    _config["handlers"]["file"]["filename"] = f"{_LOGGER_NAME}.log"

    logging.config.dictConfig(config=_config)
    _logger.debug("Logging configuration loaded successfully")


def get_logger() -> Logger:
    """
    Returns the logger to the user

    :return: The `Logger` object
    """
    return _logger


_setup_logging()
