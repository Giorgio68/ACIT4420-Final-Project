# pylint: disable=invalid-name
"""
This package is used to plan an efficient path between all of Tarjan's relatives. Package written
by Giorgio Salvemini for part one of the final project of ACIT4420
"""

from pathlib import Path
from .logger import get_logger
from .relatives_manager import RelativesManager
from .compute_route import calculate_route, display_route, save_route
from .exceptions import RouteCalculationError, RouteDisplayingError


__all__ = [
    "get_logger",
    "RelativesManager",
    "calculate_route",
    "display_route",
    "start",
    "RouteCalculationError",
    "RouteDisplayingError",
    "start",
]


def menu() -> int:
    """
    Displays a user choice menu
    """

    while True:
        print(
            """
***********************************
* 1. Import relatives             *
* 2. Add new relative             *
* 3. List all relatives           *
* 4. Calculate an optimal route   *
* 5. Display the calculated route *
* 6. Save calculated route        *
* 0. Exit                         *
***********************************
"""
        )

        try:
            user_choice = int(input("What would you like to do?: "))
            if 0 <= user_choice <= 6:
                return user_choice

        except ValueError:
            print("Please insert a valid choice")


def start() -> None:
    """
    Program entrypoint. Launches main menu
    """

    logger = get_logger()

    while True:
        user_input = menu()

        # import contacts
        if user_input == 1:
            rm = RelativesManager(json_fname=Path(".") / "data" / "relatives.jsonl")
            print("Imported relatives list")

        # manually add new contact
        elif user_input == 2:
            if "rm" not in locals():
                logger.warning("You must use option 1 first!")
                continue

            name = input("What is your relative's name?: ")
            district = input("What is your relative's district?: ")

            try:
                lat = float(input("What is your relative's latitude?: "))

            except ValueError:
                logger.error("You must input an integer/float!")

            try:
                lon = float(input("What is your relative's longitude?: "))

            except ValueError:
                logger.error("You must input an integer/float!")

            rm.add_relative(name, district, lat, lon)
            print("Added new relative")

        # list all relatives
        elif user_input == 3:
            if "rm" not in locals():
                print("You must use option 1 first!")
                continue

            rm.list_relatives()

        # compute route
        elif user_input == 4:
            if "rm" not in locals():
                logger.warning("You must use option 1 first!")
                continue

            # note that the first set corresponds to an address near Han River in Seoul,
            # i.e. Tarjan's home address
            fig = calculate_route(
                (37.52631701766444, 126.9326773050091), rm.get_relatives()
            )
            print("Route calculated")

        # display route
        elif user_input == 5:
            if "fig" not in locals():
                logger.warning("You must use option 4 first!")
                continue

            display_route(fig)

        # save plotted route
        elif user_input == 6:
            if "fig" not in locals():
                logger.warning("You must use option 4 first!")
                continue

            save_route(fig)
            print("Route saved")

        # quit
        elif user_input == 0:
            print("Goodbye!")
            logger.info("Quitting program")
            break
