"""
This module is used to manage a list of contacts, from a list, CSV, JSON or text file
"""

import re
import json
from pathlib import Path
from typing import Optional
from .logger import get_logger
from .exceptions import RMSetupFailed, RMAddRelativeFaiied


class Singleton(type):
    """
    Ensure we cannot instantiate a class more than once
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RelativesManager(metaclass=Singleton):
    """
    Class used to store and manage a list of relatives. Relatives can either be added by providing
    a list, or a jsonl filename

    :param relatives_list: A list of relatives, if provided
    :param json_fname: A JSONL file to extract relatives from
    """

    def __init__(
        self,
        relatives_list: Optional[list] = None,
        json_fname: Optional[str | list[str] | Path | list[Path]] = None,
    ) -> None:
        """
        Constructor method
        """

        self._relatives = []
        self._logger = get_logger()

        if not relatives_list and not json_fname:
            self._logger.critical("No relatives have been provided")
            raise RMSetupFailed(
                "No relatives have been provided!",
                additional_info="Either a list or json filename must be given",
            )

        if relatives_list:
            for relative in relatives_list:
                self.add_relative(**relative)

        if json_fname:
            # we expect a jsonl file here
            try:
                with open(json_fname, "r", encoding="utf-8") as f_json:
                    # makes a list of each line (a.k.a. each json stored)
                    json_list = list(f_json)

                    for json_str in json_list:
                        json_dict = json.loads(json_str)
                        self.add_relative(**json_dict)

            except FileNotFoundError as e:
                self._logger.error(
                    "An invalid filename was given for the relatives' list"
                )
                raise RMSetupFailed(
                    "An invalid filename for the relatives' list has been given",
                    additional_info=f"File name: {json_fname}",
                ) from e

    def add_relative(
        self,
        name: str,
        street_name: str,
        district: str,
        latitude: float,
        longitude: float,
    ) -> None:
        """
        This method allows a user to add a new contact to the contact list

        :param name: The relative's name
        :param district: The relative's district
        :param latitude: The relative's latitude
        :param longitude: The relative's longitude
        """

        for relative in self._relatives:
            if relative["name"] == name:
                self._logger.warning("Contact %s exists already", name)
                return

        # check that latitude and longitude are floats as expected
        if not re.match(r"[+-]?([0-9]*[.])?[0-9]+", str(latitude)):
            self._logger.error("An invalid latitude was provided")
            raise RMAddRelativeFaiied("An invalid latitude was provided")

        if not re.match(r"[+-]?([0-9]*[.])?[0-9]+", str(longitude)):
            self._logger.error("An invalid longitude was provided")
            raise RMAddRelativeFaiied("An invalid longitude was provided")

        relative = {
            "name": name,
            "street_name": street_name,
            "district": district,
            "latitude": latitude,
            "longitude": longitude,
        }
        self._relatives.append(relative)
        self._logger.info("Added relative to list: %s", relative)

    def get_relative(self, name: str) -> dict[str] | None:
        """
        Retrieves a specified relative. Note that the contact relative is a reference, not a copy

        :param name: The relative to retrieve
        :return: The `dict` object storing the relative itself, or `None` if no contact is found
        """
        for relative in self._relatives:
            if relative["name"] == name:
                return relative

        self._logger.warning("Relative %s does not exist", name)
        return None

    def get_relatives(self) -> list[dict]:
        """
        Returns the list of relatives

        :return: The contacts
        """
        return self._relatives

    def list_relatives(self) -> None:
        """
        Prints a formatted list of all relatives and their details
        """
        for relative in self._relatives:
            print(
                f"Name: {relative['name']},"
                f"Street name: {relative['street_name']},"
                f"District: {relative['district']},"
                f"Lat, Lon: {relative['latitude']}, {relative['longitude']}"
            )

    def __repr__(self) -> str:
        repr_str = ""

        for relative in self._relatives:
            repr_str += f"Name: {relative['name']},"
            repr_str += f"Street name: {relative['street_name']},"
            repr_str += f"District: {relative['district']},"
            repr_str += f"Lat, Lon: {relative['latitude']}, {relative['longitude']}\n"

        return repr_str

    def __str__(self) -> str:
        repr_str = ""

        for relative in self._relatives:
            repr_str += f"Name: {relative['name']},"
            repr_str += f"Street name: {relative['street_name']},"
            repr_str += f"District: {relative['district']},"
            repr_str += f"Lat, Lon: {relative['latitude']}, {relative['longitude']}\n"

        return repr_str

    def __bool__(self) -> bool:
        return bool(self._relatives)
