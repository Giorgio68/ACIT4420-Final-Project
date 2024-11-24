"""
Module used to compute and display the most efficient route between relatives
"""

import re
import json
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from geopy.distance import geodesic
from .logger import get_logger
from .decorators import log_func_call, time_func_call, cache
from .exceptions import ModesImportFailed, RouteCalculationError, RouteDisplayingError


_modes_of_transport: dict[str | float] = None
_logger = get_logger()


def _load_modes(f_name: Optional[Path] = None) -> None:
    global _modes_of_transport  # pylint: disable=global-statement

    if f_name is None:
        f_name = Path(".") / "data" / "mode_of_transport.json"

    try:
        with open(f_name, "rb") as f_json:
            _modes_of_transport = json.loads(f_json.read())

        for _, mode in _modes_of_transport.items():
            if not re.match(r"[+-]?([0-9]*[.])?[0-9]+", str(mode["speed"])):
                _logger.critical('"speed" is stored incorrectly')
                raise ModesImportFailed('param "speed" is not a number')

            if not re.match(r"[+-]?([0-9]*[.])?[0-9]+", str(mode["cost_per_km"])):
                _logger.critical('"cost_per_km" is stored incorrectly')
                raise ModesImportFailed('param "cost_per_km" is not a number')

            if not re.match(r"[+-]?([0-9]*[.])?[0-9]+", str(mode["transfer_time_min"])):
                _logger.critical('"transfer_time_min" is stored incorrectly')
                raise ModesImportFailed('param "transfer_time_min" is not a number')

    except (FileNotFoundError, ModesImportFailed) as e:
        _logger.critical("Modes of transport have been stored incorrectly")
        raise ModesImportFailed("Failed to import modes of transport") from e


_load_modes()


@log_func_call
@time_func_call
@cache
def calculate_route(start_point: set[float], relatives: list[dict]) -> Figure:
    """
    Calculate the most time efficient route to visit all relatives, and plot it

    :param start_point: Where the plotting should start from, i.e. Tarjan's house's coordinates
    :param relatives: The list of relatives
    :return: The calculated route
    """

    fig = plt.figure()

    coordinates = [start_point]

    for relative in relatives:
        coordinates.append({relative["latitude"], relative["longitude"]})

    x, y = zip(*coordinates)

    # add labels
    plt.title("Tarjan's efficient path for gift deliverying")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    # plot the coordinates
    plt.scatter(x, y, color="blue")

    # connect all locations
    plt.plot(x, y, color="red")

    _logger.info("Route calculated")

    return fig


@log_func_call
def display_route(plot: Figure) -> None:
    """
    Display the calculated route to the user

    :param plot: The figure to be displayed
    """

    try:
        plot.show()
        _logger.info("Opened new window showing plot")

    except Exception as e:
        raise RouteDisplayingError("Couldn't display the route") from e


@log_func_call
def save_route(plot: Figure, file_name: Optional[str | Path] = None) -> None:
    """
    Save a given plot to the current user directory

    :param plot: The plotted route to be saved
    :param file_name: An optional file name, if the user wishes to give their files a different name
    """

    fname = file_name if file_name else "efficient_route"

    plot.savefig(f"{fname}.svg", format="svg")

    _logger.info("Route saved")
