# pylint: disable=invalid-name
"""
This package is used to plan an efficient path between all of Tarjan's relatives. Package written
by Giorgio Salvemini as the final project of ACIT4420
"""

from .logger import get_logger
from .relatives_manager import RelativesManager

__all__ = ["get_logger", "RelativesManager"]
