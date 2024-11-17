# pylint: disable=invalid-name
"""
This package is used to plan an efficient path between all of Tarjan's relatives. Package written
by Giorgio Salvemini as the final project of ACIT4420
"""

from .logger import get_logger
from .relatives_manager import RelativesManager
from .compute_route import calculate_route, display_route
from .exceptions import RouteCalculationError, RouteDisplayingError


__all__ = [
    "get_logger",
    "RelativesManager",
    "calculate_route",
    "display_route",
    "start",
    "RouteCalculationError",
    "RouteDisplayingError",
]


def start() -> None:
    """
    Program entrypoint. Launches main menu
    """
