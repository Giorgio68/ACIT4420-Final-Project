"""
Module used to compute and display the most efficient route between relatives
"""

import json
from pathlib import Path
from typing import Optional
from .exceptions import ModesImportFailed, RouteCalculationError, RouteDisplayingError


_modes_of_transport: dict[str | float] = None


def _load_modes(f_name: Optional[Path] = None) -> None:
    global _modes_of_transport  # pylint: disable=global-statement

    if f_name is None:
        f_name = Path(".") / "data" / "mode_of_transport.json"

    try:
        with open(f_name, "rb") as f_json:
            _modes_of_transport = json.loads(f_json)

    except FileNotFoundError as e:
        raise ModesImportFailed("Failed to import modes of transport") from e


_load_modes()


def calculate_route():
    pass


def display_route():
    pass
