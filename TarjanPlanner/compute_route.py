"""
Module used to compute and display the most efficient route between relatives
"""

import json
from pathlib import Path
from typing import Optional


_MODES_OF_TRANSPORT: dict[str | float] = None

def _load_modes(f_name: Optional[Path] = None) -> None:
    if f_name is None:
        f_name = Path(".") / "data" / "mode_of_transport.json"

    with open(f_name, "r", encoding="utf-8") as f_json:
        _MODES_OF_TRANSPORT.append(json.loads(f_json))


_load_modes()


def compute_route():
    pass


def display_route():
    pass
