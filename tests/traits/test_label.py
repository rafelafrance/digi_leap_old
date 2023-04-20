import unittest

from tests.setup import test


class TestLabels(unittest.TestCase):
    def test_label_01(self):
        self.assertEqual(
            test(
                """
                Tarleton State University Herbarium (TAC) Cornus obliqua (Benth)
                Texas, Mason County: Mason: 5 miles North of Mason off Hwy 386. Mason
                Mountains Wildlife Management Area. Grassland,
                GPS 30° 49’ 27’ N, 99" 15' 22 W May 19, 1998 HR1998-01 H. Richey
                """
            ),
            [
                {
                    "taxon": "Cornus obliqua",
                    "rank": "species",
                    "authority": "Benth",
                    "trait": "taxon",
                    "start": 42,
                    "end": 64,
                },
                {
                    "us_state": "Texas",
                    "us_county": "Mason",
                    "trait": "admin_unit",
                    "start": 65,
                    "end": 84,
                },
                {"habitat": "grassland", "trait": "habitat", "start": 171, "end": 180},
                {
                    "lat_long": "30° 49’ 27’ N, 99\" 15' 22 W",
                    "trait": "lat_long",
                    "start": 182,
                    "end": 213,
                },
                {"date": "1998-05-19", "trait": "date", "start": 214, "end": 226},
                {
                    "collector_no": "HR1998-01",
                    "collector": "H. Richey",
                    "trait": "collector",
                    "start": 227,
                    "end": 246,
                },
            ],
        )

    def test_label_02(self):
        self.assertEqual(
            test(
                """
                Fraijanes, Alaeloa Costa Rica
                Cornaceae
                Cornus obliqua Willd.
                In Fraijanes Recreation Park, at 1475 m in
                tropical cloud forest, volcanic area with
                acid soil, 2-3 m tall.
                William M. Houghton 531 14 Jan. 1987
                collected by Merle Dortmond
                The University of Georgia Athens, GA, U.S.A.
                """
            ),
            [
                {
                    "associated_taxon": "Cornaceae",
                    "trait": "associated_taxon",
                    "rank": "family",
                    "start": 30,
                    "end": 39,
                },
                {
                    "taxon": "Cornus obliqua",
                    "trait": "taxon",
                    "authority": "Willd",
                    "rank": "species",
                    "start": 40,
                    "end": 60,
                },
                {
                    "habitat": "tropical cloud forest",
                    "trait": "habitat",
                    "start": 105,
                    "end": 126,
                },
                {
                    "collector_no": "531",
                    "collector": "William M. Houghton",
                    "trait": "collector",
                    "start": 170,
                    "end": 193,
                },
                {
                    "date": "1987-01-14",
                    "trait": "date",
                    "start": 194,
                    "end": 206,
                },
                {
                    "collector": "Merle Dortmond",
                    "trait": "collector",
                    "start": 207,
                    "end": 234,
                },
            ],
        )
