"""
A file organizer. Package written by Giorgio Salvemini for part two of the final project of ACIT4420
"""

from .file_types import files
from .logger import get_logger
from .sort_files import sort


__all__ = ["start", "files", "get_logger", "sort"]


def menu() -> int:
    """
    Displays a user choice menu
    """

    while True:
        print(
            """
********************************
* 1. Add a new type            *
* 2. Show supported file types *
* 3. Sort files                *
* 0. Exit                      *
********************************
"""
        )

        try:
            user_choice = int(input("What would you like to do?: "))
            if 0 <= user_choice <= 3:
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
            file_type = input("What file type do you want to add?: ")
            ext = input(
                "What extension should this type have? (write each separated with a space): "
            )

            files[file_type] = {"extension": ext.split()}

            print("Added new file type: {file_type}")

        # show supported types
        elif user_input == 2:
            for k, v in files.items():
                print(f"Type: {k}, extensions: {v['extension']}")

        # sort files
        elif user_input == 3:
            directory = input(
                "Which directory would you like to sort? (press enter for the current directory): "
            )
            if not directory:
                directory = "./test"

            sort(directory)

        # quit
        elif user_input == 0:
            print("Goodbye!")
            logger.info("Quitting program")
            break
