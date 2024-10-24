"""
This module is used to manage a list of contacts, from a list, CSV, JSON or text file
"""

import json
from pathlib import Path
from typing import Optional
from .logger import get_logger


class RelativesManager:
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

        if relatives_list:
            self._relatives.extend(relatives_list)
            self._logger.info("Added relatives to list: %s", relatives_list)

        if json_fname:
            # we expect a jsonl file here
            with open(json_fname, "r", encoding="utf-8") as f_json:
                # makes a list of each line (a.k.a. each json stored)
                json_list = list(f_json)

                for json_str in json_list:
                    json_dict = json.loads(json_str)
                    self._relatives.append(json_dict)

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
                f"District: {relative['district']},"
                f"Lat, Lon: {relative['latitude']}, {relative['longitude']}"
            )

    def __repr__(self) -> str:
        repr_str = ""

        for relative in self._relatives:
            repr_str += f"Name: {relative['name']},"
            repr_str += f"District: {relative['district']},"
            repr_str += f"Lat, Lon: {relative['latitude']}, {relative['longitude']}\n"

        return repr_str

    def __str__(self) -> str:
        repr_str = ""

        for relative in self._relatives:
            repr_str += f"Name: {relative['name']},"
            repr_str += f"District: {relative['district']},"
            repr_str += f"Lat, Lon: {relative['latitude']}, {relative['longitude']}\n"

        return repr_str

    def __bool__(self) -> bool:
        return bool(self._relatives)
