import unittest

from tests.setup import test


class TestLatLongPatterns(unittest.TestCase):

    # def test_lat_long_00(self):
    #     test("""117° 15.606' 7.5\"""")

    def test_lat_long_01(self):
        self.assertEqual(
            test("""Grassland, GPS 30° 49’ 27’ N, 99" 15' 22 W May"""),
            [
                {"habitat": "grassland", "trait": "habitat", "start": 0, "end": 9},
                {
                    "lat_long": """30° 49’ 27’ N, 99" 15' 22 W""",
                    "trait": "lat_long",
                    "start": 11,
                    "end": 42,
                },
            ],
        )

    def test_lat_long_02(self):
        self.assertEqual(
            test("""floodplain wetland. 40.104905N, 79.324561W NAD83"""),
            [
                {
                    "end": 18,
                    "habitat": "floodplain wetland",
                    "start": 0,
                    "trait": "habitat",
                },
                {
                    "lat_long": """40.104905 N, 79.324561 W""",
                    "trait": "lat_long",
                    "datum": "NAD83",
                    "start": 20,
                    "end": 48,
                },
            ],
        )

    def test_lat_long_03(self):
        self.assertEqual(
            test("""32° 19.517' N 110° 40.242' W Elev: 1217m"""),
            [
                {
                    "lat_long": """32° 19.517' N 110° 40.242' W""",
                    "trait": "lat_long",
                    "start": 0,
                    "end": 28,
                }
            ],
        )
