"""Test trait extraction on labels."""
import unittest

from tests.setup import test


class TestLabels(unittest.TestCase):
    """Test trait extraction on labels."""

    def test_label_00(self):
        test(
            """
            Fraijanes, Alaeloa Costa Rica
            Myricaceae
            Myrica pubescens Willd.
            In Fraijanes Recreation Park, at 1475 m in
            tropical cloud forest, volcanic area with
            acid soil, 2-3 m tall.
            William M. Houghton 531 14 Jan. 1987
            collected by Merle Dortmond
            The University of Georgia Athens, GA, U.S.A.
         """
        )

    def test_label_01(self):
        """County vs colorado (CO)."""
        self.assertEqual(
            test(
                """
                    PLANTS OF FLORIDA
                    Cyperus
                    aculeatus
                    CHARLOTTE CO.: Prairie / Shell Creek(SFM
                    property); 0.05 km W of US 17, 1.3 km S of Sam
                    Way:
                    26° 59’21" N, 81° 57' 35" W.
                    Ruderal depression:
                    Alan R. Franck 2523
                    4 December 2010
                    UNIVERSITY OF SOUTH FLORIDA HERBARIUM
                """
            ),
            [
                {"us_state": "Florida", "trait": "admin_unit", "start": 0, "end": 17},
                {
                    "genus": "Cyperus",
                    "species": "aculeatus",
                    "trait": "taxon",
                    "start": 18,
                    "end": 35,
                },
                {
                    "us_county": "Charlotte",
                    "trait": "admin_unit",
                    "start": 36,
                    "end": 49,
                },
                {
                    "collector_no": "2523",
                    "collector": "Alan R. Franck",
                    "trait": "collector",
                    "start": 176,
                    "end": 197,
                },
                {
                    "label_date": "2010-12-04",
                    "trait": "label_date",
                    "start": 198,
                    "end": 213,
                },
            ],
        )
