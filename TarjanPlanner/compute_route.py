"""
Module used to compute and display the most efficient route between relatives
"""

# import general libraries
import re
import json
from copy import deepcopy
from pathlib import Path
from typing import Optional

# graph and tsp solver
import networkx as nx
from networkx import Graph
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

        for mode in _modes_of_transport.values():
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
def _initialize_complete_graph(points: list[tuple]) -> Graph:
    """
    Creates an instance of a `networkx.Graph`, initialized it with nodes and edges, and returns it.
    N.B. This method differs from `_initialize_complete_graph` in the inserted edges: the graph
    produced by this function is "complete", i.e. every node is connected to every other node on
    the graph.

    :param points: The list of nodes to be drawn
    :return: The initialized graph
    """

    graph = Graph()

    for i, point in enumerate(points):
        graph.add_node(i, pos=point)

    # edges represent the transportation network between relatives and Tarjan
    for i in range(len(points)):  # pylint: disable=consider-using-enumerate
        for j in range(i + 1, len(points)):
            travel_time = {
                mode: _calculate_travel_time(
                    (points[i][1], points[i][0]), (points[j][1], points[j][0]), mode
                )
                for mode in _modes_of_transport
            }

            optimal_mode = min(travel_time, key=travel_time.get)
            graph.add_edge(i, j, weight=travel_time[optimal_mode])
            graph[i][j]["travel_time"] = travel_time[optimal_mode]
            graph[i][j]["mode_of_transport"] = optimal_mode

            _logger.debug("Travel time: %s", travel_time)
            _logger.debug("Optimal mode: %s", optimal_mode)
            _logger.debug(
                "Travel time using optimal mode: %s", travel_time[optimal_mode]
            )

    return graph


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

        travel_distance = _calculate_distance_km(
            (points[start][1], points[start][0]), (points[end][1], points[end][0])
        )

        graph.add_edge(start, end, weight=travel_time)
        graph[start][end]["travel_time"] = travel_time
        graph[start][end]["travel_distance"] = travel_distance
        graph[start][end]["mode_of_transport"] = mode

        _logger.debug("Distance: %s", travel_distance)
        _logger.debug("Travel mode: %s", mode)

    _logger.info("Graph has been initialized")

    return graph


# pylint: disable=invalid-name
@time_func_call
def _dfs_tsp(G: Graph, weight: str = "weight") -> list[int]:
    """
    This method implements a depth-first search algorithm to find the best solution to the
    traveling salesman problem. The nodes and edges used are those that have been created during
    the graph's initialization. This algorithm uses recursion, which makes it unsuitable for routes
    with a lot of nodes (>1000) as it will hit python's recursion limit. Time complexity is
    O(|V|+|E|), where |V| is the number of nodes and |E| is the number of edges

    :param G: The graph to be used to find the best possible path
    :param weight: The weight to be used to determine the best path
    :return: The solution to the TSP, as a list of integers matching each node in the path
    """

    best_route = [0]
    shortest_time = float("inf")

    def recurse_tree(G: Graph, node: int, route: list) -> None:
        if len(route[0]) == G.number_of_nodes():
            nonlocal shortest_time, best_route
            if route[1] < shortest_time:
                shortest_time = route[1]
                best_route = route[0]

                _logger.debug(
                    "Newest shortest route is %.2f, best route is %s",
                    shortest_time,
                    best_route,
                )

            return

        for next_node, data in G[node].items():
            if next_node in route[0]:
                continue

            route_copy = deepcopy(route)
            route_copy[0].append(next_node)
            route_copy[1] += data[weight]

            recurse_tree(G, next_node, route_copy)

    recurse_tree(G, 0, [best_route, 0])

    return best_route


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

    optimal_route = _dfs_tsp(graph)

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

        # draw the points and label them
        pos = {i: point for i, point in enumerate(coordinates)}
        node_colors = ["orange"]
        for i in range(len(relatives)):
            node_colors.append("cyan")

        nx.draw_networkx_nodes(graph, pos, node_size=100, node_color=node_colors)

        labels = {0: "Tarjan"}
        for i, relative in enumerate(relatives):
            labels[i + 1] = relative["street_name"]

        nx.draw_networkx_labels(graph, pos, labels, font_size=6)

        # draw the route
        optimal_route_edges = [
            (optimal_route[i], optimal_route[i + 1])
            for i in range(len(optimal_route) - 1)
        ]
        edge_colors = [
            legend.get(graph[u][v]["mode_of_transport"], "brown") for u, v in optimal_route_edges
        ]

        total_travel_time = sum(
            graph[i][j]["travel_time"]
            for i, j in zip(optimal_route[:-1], optimal_route[1:])
        )

        travel_distances = {
            edge: _calculate_distance_km(
                (optimal_route_points[i][1], optimal_route_points[i][0]),
                (optimal_route_points[i + 1][1], optimal_route_points[i + 1][0]),
            )
            for edge, i in zip(
                optimal_route_edges, range(len(optimal_route_points) - 1)
            )
        }

        total_travel_distance = sum(
            distance for _, distance in travel_distances.items()
        )

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
            nx.draw_networkx_edge_labels(
                graph,
                pos,
                edge_labels={target: f"{travel_distances[target]:.2f} Km"},
                font_size=6,
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
        f.write(str(optimal_route))

    plot.savefig(f"{fname}.svg", format="svg", bbox_inches="tight")

    _logger.info("Route saved")
