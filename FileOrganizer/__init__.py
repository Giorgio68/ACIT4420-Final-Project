"""
A file organizer. Package written by Giorgio Salvemini for part two of the final project of ACIT4420
"""


from .file_types import types
from .logger import get_logger


__all__ = ["start", "types", "get_logger"]


def menu() -> int:
    """
    Displays a user choice menu
    """

    while True:
        print(
            """
*********************
* 1. Add a new type *
* 2. Sort files     *
* 0. Exit           *
*********************
"""
        )

        try:
            user_choice = int(input("What would you like to do?: "))
            if 0 <= user_choice <= 2:
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

        # add new type
        if user_input == 1:
            pass

        # sort list
        elif user_input == 2:
            pass

        # quit
        elif user_input == 0:
            print("Goodbye!")
            logger.info("Quitting program")
            break
