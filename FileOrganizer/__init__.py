"""
A file organizer. Package written by Giorgio Salvemini for part two of the final project of ACIT4420
"""


from .file_types import types
from .logger import get_logger


__all__ = [
    "start",
    "types",
    "get_logger"
]


def start():
    """
    Main program entrypoint
    """
