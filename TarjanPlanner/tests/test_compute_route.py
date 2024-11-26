"""
Tests the `compute_route` module
"""

import unittest
from ..exceptions import ModesImportFailed
from ..compute_route import _calculate_distance_km, _calculate_travel_time, _load_modes


class Test(unittest.TestCase):
    def test_import_modes(self):
        self.assertRaises(
            ModesImportFailed, _load_modes, "invalid_path_modes", "invalid_path_route"
        )
        _load_modes()

    def test_calculate_distance(self):
        distance = _calculate_distance_km((59.9194, 10.7353), (59.9390, 10.7450))
        self.assertIsInstance(distance, float)
        self.assertAlmostEqual(distance, 2.25, places=4)

    def test_calculate_travel_time(self):
        time_traveled = _calculate_travel_time(
            (59.9194, 10.7353), (59.9390, 10.7450), "bus"
        )
        self.assertAlmostEqual(time_traveled, (2.25 / 40) * 60 + 5, places=4)


if __name__ == "__main__":
    unittest.main()
