"""
Tests the `relatives_manager` module
"""

import unittest
from pathlib import Path
from ..exceptions import RMAddRelativeFailed
from ..relatives_manager import RelativesManager


relatives_folder = Path(".") / "data"

relatives_manager = RelativesManager(json_fname=relatives_folder / "relatives.jsonl")


class TestContactManager(unittest.TestCase):
    def test_print_contacts(self):
        print(repr(relatives_manager))
        print(relatives_manager.get_relatives())

    def test_new_contact(self):
        relatives_manager.add_relative(
            "New relative",
            "pilestredet 35",
            "oslo",
            59.91942076527345,
            10.735377778022945,
        )
        print(relatives_manager.get_relatives())

        # make sure it errors when not passing valid parameters
        self.assertRaises(
            RMAddRelativeFailed,
            relatives_manager.add_relative,
            "",
            "pilestredet 52",
            "oslo",
            59.91942076527345,
            10.735377778022945,
        )
        self.assertRaises(
            RMAddRelativeFailed,
            relatives_manager.add_relative,
            "George",
            "",
            "oslo",
            59.91942076527345,
            10.735377778022945,
        )
        self.assertRaises(
            RMAddRelativeFailed,
            relatives_manager.add_relative,
            "George",
            "filipstadveien 7",
            "",
            59.91942076527345,
            10.735377778022945,
        )
        self.assertRaises(
            RMAddRelativeFailed,
            relatives_manager.add_relative,
            "George",
            "pilestredet 46",
            "oslo",
            59.91942076527345,
            "invalid longitude",
        )
        self.assertRaises(
            RMAddRelativeFailed,
            relatives_manager.add_relative,
            "George",
            "pilestredet 46",
            "oslo",
            "invalid latitude",
            10.735377778022945,
        )

        # make sure duplicates cannot be added
        relatives_manager.add_relative(
            "New relative",
            "pilestredet 35",
            "oslo",
            59.91942076527345,
            10.735377778022945,
        )
        print(relatives_manager.get_relatives())

    def test_get_contacts(self):
        print(relatives_manager.get_relatives())

    def test_boolean(self):
        self.assertTrue(bool(relatives_manager))

    def test_get_contact(self):
        self.assertTrue(relatives_manager.get_relative("Relative_1") is not None)
        self.assertTrue(relatives_manager.get_relative("Invalid name") is None)


if __name__ == "__main__":
    unittest.main()
