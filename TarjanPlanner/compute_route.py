"""
Module used to compute and display the most efficient route between relatives
"""

import re
import json
from pathlib import Path
from typing import Optional
from .exceptions import ModesImportFailed, RouteCalculationError, RouteDisplayingError
from .decorators import log_func_call, time_func_call, cache


_modes_of_transport: dict[str | float] = None


def _load_modes(f_name: Optional[Path] = None) -> None:
    global _modes_of_transport  # pylint: disable=global-statement

    if f_name is None:
        f_name = Path(".") / "data" / "mode_of_transport.json"

    try:
        with open(f_name, "rb") as f_json:
            _modes_of_transport = json.loads(f_json)

        for mode in _modes_of_transport:
            if not re.match(r"[+-]?([0-9]*[.])?[0-9]+", mode["speed"]):
                raise ModesImportFailed('param "speed" is not a number')

            if not re.match(r"[+-]?([0-9]*[.])?[0-9]+", mode["cost_per_km"]):
                raise ModesImportFailed('param "cost_per_km" is not a number')

            if not re.match(r"[+-]?([0-9]*[.])?[0-9]+", mode["transfer_time_min"]):
                raise ModesImportFailed('param "transfer_time_min" is not a number')

    except (FileNotFoundError, ModesImportFailed) as e:
        raise ModesImportFailed("Failed to import modes of transport") from e


_load_modes()


@log_func_call
@time_func_call
@cache
def calculate_route():
    pass


@log_func_call
def display_route():
    pass
