"""
Module used to compute and display the most efficient route between relatives
"""

# import general libraries
import re
import json
from pathlib import Path
from typing import Optional

# graph and tsp solver
import networkx as nx
from networkx import Graph
from networkx.algorithms.approximation import traveling_salesman_problem as tsp
from networkx.algorithms.approximation.traveling_salesman import greedy_tsp
from geopy.distance import geodesic

# plot
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Patch

# local function
from .logger import get_logger
from .decorators import log_func_call, time_func_call, cache
from .exceptions import ModesImportFailed, RouteCalculationError, RouteDisplayingError


_modes_of_transport: dict[str, dict[str, float]] = None
_transport_network: dict[tuple[int, int], str] = None
_logger = get_logger()


# pylint: disable=too-many-branches,global-statement
@log_func_call
def _load_modes(
    f_name_modes: Optional[str | Path] = None,
    f_name_routes: Optional[str | Path] = None,
) -> None:
    global _modes_of_transport
    global _transport_network

    # load modes of transport
    if f_name_modes is None:
        f_name_modes = Path(".") / "data" / "mode_of_transport.json"

    if not isinstance(f_name_modes, Path):
        f_name_modes = Path(f_name_modes)

    try:
        with open(f_name_modes, "rb") as f_modes:
            _modes_of_transport = json.loads(f_modes.read())

        for _, mode in _modes_of_transport.items():
            # check that these values are all floats
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

    # load routes
    if f_name_routes is None:
        f_name_routes = Path(".") / "data" / "transport_network.json"

    if not isinstance(f_name_routes, Path):
        f_name_routes = Path(f_name_routes)

    try:
        with open(f_name_routes, "rb") as f_routes:
            temp_network = json.loads(f_routes.read())

        _transport_network = {}

        # ensure that both the route name and mode of transport are correct
        for route, mode in temp_network.items():
            if not re.match(r"^\d \d{1,2}$", route):
                _logger.critical("Route %s has been stored incorrectly", route)
                raise ModesImportFailed(
                    f"Route {route} is not in format '<number> <number>'"
                )

            if mode not in _modes_of_transport:
                _logger.critical("Mode %s is invalid. Check modes of transport", mode)
                raise ModesImportFailed(
                    f"Mode {mode} is invalid. Check modes of transport"
                )

        for route, mode in temp_network.items():
            tup_route = tuple(map(int, route.split()))
            _transport_network[tup_route] = mode

    except (FileNotFoundError, ModesImportFailed) as e:
        _logger.critical("Routes have been stored incorrectly")
        raise ModesImportFailed("Failed to import routes") from e


_load_modes()


def _calculate_distance_km(
    start: tuple[float, float], end: tuple[float, float]
) -> float:
    """
    Calculates the distance between two sets of coordinates

    :param start: The start point
    :param end: The end point
    :return: The distance in KM
    """
    return geodesic(start, end).km


def _calculate_travel_time(
    start: tuple[float, float], end: tuple[float, float], mode: str
) -> float:
    """
    Find the travel time based on the geodesic distance between two locations,
    including transfer time

    :param start: The starting coordinates, in format
    :param end: The destination to be reached
    :param mode: The mode of transport to be used
    :return: The travel time, in minutes
    """
    distance = _calculate_distance_km(start, end)
    speed = _modes_of_transport[mode]["speed"]
    transfer_time = _modes_of_transport[mode]["transfer_time_min"]

    _logger.debug("Distance from %s to %s is %.2f", start, end, distance)

    return (distance / speed) * 60 + transfer_time


@log_func_call
def _initialize_graph(points: list[tuple]) -> Graph:
    """
    Creates an instance of a `networkx.Graph`, initialized it with nodes and edges, and returns it

    :param points: The list of nodes to be drawn
    :return: The initialized graph
    """

    graph = Graph()

    for i, point in enumerate(points):
        graph.add_node(i, pos=point)

    # edges represent the transportation network between relatives and Tarjan
    for route, mode in _transport_network.items():
        start, end = route

        travel_time = _calculate_travel_time(
            (points[start][1], points[start][0]), (points[end][1], points[end][0]), mode
        )
        graph.add_edge(start, end, weight=travel_time)
        graph[start][end]["mode_of_transport"] = mode

        _logger.debug("Travel time: %s", travel_time)
        _logger.debug("Travel mode: %s", mode)

    _logger.info("Graph has been initialized")

    return graph


@time_func_call
@cache
def _find_optimal_route(points: list[tuple]) -> tuple[Graph, list[float]]:
    """
    This function uses the `networkx.algorithms.traveling_salesman_problem` function to find the
    shortest path across all points (i.e. Tarjan's house, and all his relatives). It then finds the
    fastest transportation method between each point, and uses it.

    :param points: The list of nodes to cross
    :return: A tuple containing the `networkx` graph, and the optimal route itself
    """

    graph = _initialize_graph(points)

    # cycle=True means we go back to the starting point at the end
    optimal_route = tsp(graph, cycle=True, method=greedy_tsp)

    _logger.debug("Optimal route: %s", optimal_route)

    return graph, optimal_route


@log_func_call
@time_func_call
@cache
def calculate_route(
    start_point: set[float], relatives: list[dict]
) -> tuple[Figure, list[tuple[float, float]]]:
    """
    Calculate the most time efficient route to visit all relatives, and plot it

    :param start_point: Where the plotting should start from, i.e. Tarjan's house's coordinates
    :param relatives: The list of relatives
    :return: The displayed route, and the calculated route as a list of coordinates
    """

    legend = {
        "bus": "red",
        "train": "green",
        "bicycle": "purple",
        "walking": "blue",
        "Tarjan's home": "orange",
        "Relative": "cyan",
    }

    plot_legend = [Patch(color=color, label=mode) for mode, color in legend.items()]

    fig, ax = plt.subplots()

    # note that we swap the order of lat and lon, as they will be graphed incorrectly otherwise
    coordinates = [(start_point[1], start_point[0])]
    for relative in relatives:
        coordinates.append((relative["longitude"], relative["latitude"]))

    try:
        graph, optimal_route = _find_optimal_route(coordinates)
        optimal_route_points = [coordinates[node] for node in optimal_route]

        total_travel_time = sum(
            graph[i][j]["weight"] for i, j in zip(optimal_route[:-1], optimal_route[1:])
        )

        total_travel_distance = sum(
            _calculate_distance_km(
                (optimal_route_points[i][1], optimal_route_points[i][0]),
                (optimal_route_points[i + 1][1], optimal_route_points[i + 1][0]),
            )
            for i in range(len(optimal_route_points) - 1)
        )

        # draw the points and label them
        pos = {i: point for i, point in enumerate(coordinates)}
        node_colors = ["orange"]
        for i in range(len(relatives)):
            node_colors.append("cyan")

        nx.draw_networkx_nodes(graph, pos, node_size=100, node_color=node_colors)

        labels = {0: "Tarjan"}
        for i, relative in enumerate(relatives):
            labels[i + 1] = relative["street_name"]

        nx.draw_networkx_labels(graph, pos, labels, font_size=7)

        # draw the route
        optimal_route_edges = [
            (optimal_route[i], optimal_route[i + 1])
            for i in range(len(optimal_route) - 1)
        ]
        edge_colors = [
            legend[graph[u][v]["mode_of_transport"]] for u, v in optimal_route_edges
        ]

        for target, color in zip(optimal_route_edges, edge_colors):
            nx.draw_networkx_edges(
                graph,
                pos,
                edgelist=[target],
                edge_color=color,
                width=2,
                arrows=True,
                arrowstyle="-|>",
            )

    except nx.NetworkXError as e:
        raise RouteCalculationError(
            "Networkx returned an error while calculating the optimal route"
        ) from e

    # set up the plot itself
    ax.set_title(
        "Tarjan's efficient path for gift delivering"
        f" - Total travel time: {total_travel_time:.2f} minutes"
        f" - Total distance: {total_travel_distance:.2f} Km"
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    ax.legend(handles=plot_legend, loc="upper right")
    ax.grid(True)

    _logger.info("Route calculated")

    return fig, optimal_route_points


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
def save_route(
    plot: Figure,
    optimal_route: list[tuple[float, float]],
    file_name: Optional[str | Path] = None,
) -> None:
    """
    Save a given plot to the current user directory

    :param plot: The plotted route to be saved
    :param optimal_figure: The calculated route, in coordinate format
    :param file_name: An optional file name, if the user wishes to give their files a different name
    """

    fname = file_name if file_name else "efficient_route"

    with open(f"{fname}.txt", "w", encoding="utf-8") as f:
        f.write(optimal_route)

    plot.savefig(f"{fname}.svg", format="svg")

    _logger.info("Route saved")
