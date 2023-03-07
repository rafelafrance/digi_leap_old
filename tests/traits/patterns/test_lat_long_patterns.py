import unittest

from tests.setup import test


class TestLatLongPatterns(unittest.TestCase):

    # def test_lat_long_00(self):
    #     test("""117° 15.606' 7.5\"""")

    def test_lat_long_01(self):
        self.assertEqual(
            test("""Grassland, GPS 30° 49’ 27’ N, 99" 15' 22 W May"""),
            [
                {
                    "lat_long": """GPS 30° 49’ 27’ N, 99" 15' 22 W""",
                    "trait": "lat_long",
                    "start": 11,
                    "end": 42,
                }
            ],
        )


#
