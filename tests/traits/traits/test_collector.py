import unittest

from tests.setup import test


class TestCollector(unittest.TestCase):
    def test_collector_01(self):
        """It gets a multiple name notations."""
        self.assertEqual(
            test("""Sarah Nunn and S. Jacobs and R. Mc Elderry 9480"""),
            [
                {
                    "collector_no": "9480",
                    "collector": ["Sarah Nunn", "S. Jacobs", "R. Mc Elderry"],
                    "trait": "collector",
                    "start": 0,
                    "end": 47,
                }
            ],
        )

    def test_collector_02(self):
        """It does not include the determiner."""
        self.assertEqual(
            test(
                """
                Det, Edwin B. Smith
                Coll. Marie P. Locke No. 5595
                """
            ),
            [
                {
                    "determiner": "Edwin B. Smith",
                    "trait": "determiner",
                    "start": 0,
                    "end": 19,
                },
                {
                    "collector_no": "5595",
                    "collector": "Marie P. Locke",
                    "trait": "collector",
                    "start": 20,
                    "end": 49,
                },
            ],
        )

    def test_collector_03(self):
        """It handles a bad name."""
        self.assertEqual(
            test("""Collected by _Wayne.. Hutchins."""),
            [
                {
                    "collector": "Wayne Hutchins",
                    "trait": "collector",
                    "start": 0,
                    "end": 30,
                },
            ],
        )

    def test_collector_04(self):
        """It handles random words matching names."""
        self.assertEqual(
            test("""Collected by _Wayne.. Hutchins."""),
            [
                {
                    "collector": "Wayne Hutchins",
                    "trait": "collector",
                    "start": 0,
                    "end": 30,
                },
            ],
        )

    def test_collector_05(self):
        """It parses name suffixes."""
        self.assertEqual(
            test("Coll. E. E. Dale, Jr. No. 6061"),
            [
                {
                    "collector_no": "6061",
                    "collector": "E. E. Dale, Jr.",
                    "trait": "collector",
                    "start": 0,
                    "end": 30,
                },
            ],
        )

    def test_collector_06(self):
        """It parses collectors separated by 'with'."""
        self.assertEqual(
            test("Sarah Nunn with Angela Brown 7529 20 October 2002 of"),
            [
                {
                    "collector_no": "7529",
                    "collector": ["Sarah Nunn", "Angela Brown"],
                    "trait": "collector",
                    "start": 0,
                    "end": 33,
                },
                {
                    "date": "2002-10-20",
                    "trait": "date",
                    "start": 34,
                    "end": 49,
                },
            ],
        )

    def test_collector_07(self):
        """It parses collectors separated by '&'."""
        self.assertEqual(
            test("""Collector: Christopher Reid & Sarah Nunn 2018"""),
            [
                {
                    "collector_no": "2018",
                    "collector": ["Christopher Reid", "Sarah Nunn"],
                    "trait": "collector",
                    "start": 0,
                    "end": 45,
                },
            ],
        )

    def test_collector_08(self):
        """It handles a number sign."""
        self.assertEqual(
            test("""George P. Johnson #5689"""),
            [
                {
                    "collector_no": "5689",
                    "collector": "George P. Johnson",
                    "trait": "collector",
                    "start": 0,
                    "end": 23,
                }
            ],
        )

    def test_collector_09(self):
        """It handles a name with a prefix."""
        self.assertEqual(
            test("""Col Mrs. Jim Miller No. 736"""),
            [
                {
                    "collector_no": "736",
                    "collector": "Mrs. Jim Miller",
                    "trait": "collector",
                    "start": 0,
                    "end": 27,
                }
            ],
        )

    def test_collector_10(self):
        self.assertEqual(
            test("""collected by Merle Dortmond"""),
            [
                {
                    "collector": "Merle Dortmond",
                    "trait": "collector",
                    "start": 0,
                    "end": 27,
                }
            ],
        )

    def test_collector_11(self):
        self.assertEqual(
            test(""" Grassland, GPS 30°"""),
            [{"habitat": "grassland", "trait": "habitat", "start": 0, "end": 9}],
        )

    def test_collector_12(self):
        self.assertEqual(
            test("""3807708N Elev: 1689m."""),
            [
                {
                    "elevation": 1689.0,
                    "units": "m",
                    "trait": "elevation",
                    "start": 9,
                    "end": 21,
                }
            ],
        )

    def test_collector_13(self):
        self.assertEqual(
            test("""TIMON, R16W,"""),
            [],
        )

    def test_collector_14(self):
        self.assertEqual(
            test(
                """
                Distribuido List: CRUZ, EBC, MINE
                Collector(s): Timothy J. S. Whitfield
                Collector Number: 1388 Date: 11 Aug 2016"""
            ),
            [
                {
                    "collector_no": "1388",
                    "collector": "Timothy J. S. Whitfield",
                    "trait": "collector",
                    "start": 34,
                    "end": 94,
                },
                {"date": "2016-08-11", "trait": "date", "start": 95, "end": 112},
            ],
        )

    def test_collector_15(self):
        self.assertEqual(
            test(
                """
                With: Dawn Goldman, Army Prince, Steven Emrick, Janet Smith,
                Diane Hicks, Beechnut
                """
            ),
            [
                {
                    "other_collector": [
                        "Dawn Goldman",
                        "Army Prince",
                        "Steven Emrick",
                        "Janet Smith",
                        "Diane Hicks",
                        "Beechnut",
                    ],
                    "trait": "other_collector",
                    "start": 0,
                    "end": 82,
                },
            ],
        )

    def test_collector_16(self):
        self.assertEqual(
            test("""Williams (Rocky) Gleason #F15GLEN55-B"""),
            [
                {
                    "collector_no": "F15GLEN55-B",
                    "collector": "Williams (Rocky) Gleason",
                    "trait": "collector",
                    "start": 0,
                    "end": 37,
                },
            ],
        )

    def test_collector_17(self):
        self.assertEqual(
            test(
                """
                With: Dixie Damrel, Sarah Hunkins, Steven and Johan LaMoure
                """
            ),
            [
                {
                    "other_collector": [
                        "Dixie Damrel",
                        "Sarah Hunkins",
                        "Steven and Johan LaMoure",
                    ],
                    "trait": "other_collector",
                    "start": 0,
                    "end": 59,
                },
            ],
        )

    def test_collector_18(self):
        self.assertEqual(
            test("""Frederick H. Utech 91-1178"""),
            [
                {
                    "collector_no": "91-1178",
                    "collector": "Frederick H. Utech",
                    "trait": "collector",
                    "start": 0,
                    "end": 26,
                },
            ],
        )

    def test_collector_19(self):
        self.assertEqual(
            test("""A A.C. Saunders 39141"""),
            [
                {
                    "collector_no": "39141",
                    "collector": "A A.C. Saunders",
                    "trait": "collector",
                    "start": 0,
                    "end": 21,
                },
            ],
        )

    def test_collector_20(self):
        self.assertEqual(
            test("""purple. A A.C. Saunders 39141 14 Apr 2011"""),
            [
                {"color": "purple", "end": 6, "start": 0, "trait": "color"},
                {
                    "collector_no": "39141",
                    "collector": "A A.C. Saunders",
                    "trait": "collector",
                    "start": 8,
                    "end": 29,
                },
                {"date": "2011-04-14", "end": 41, "start": 30, "trait": "date"},
            ],
        )

    def test_collector_21(self):
        """It handles names with mixed case letters."""
        self.assertEqual(
            test("""Wendy McClure 2018-2"""),
            [
                {
                    "collector_no": "2018-2",
                    "collector": "Wendy McClure",
                    "trait": "collector",
                    "start": 0,
                    "end": 20,
                },
            ],
        )

    def test_collector_22(self):
        """It handles a taxon next to a name."""
        self.assertEqual(
            test("""Associated species: Neptunia gracilis G. Rink 7075"""),
            [
                {
                    "trait": "associated_taxon",
                    "associated_taxon": "Neptunia gracilis",
                    "rank": "species",
                    "start": 20,
                    "end": 37,
                },
                {
                    "collector_no": "7075",
                    "collector": "G. Rink",
                    "trait": "collector",
                    "start": 38,
                    "end": 50,
                },
            ],
        )

    def test_collector_23(self):
        """It handles a taxon next to a name."""
        self.assertEqual(
            test("""collected by Merle Dortmond The University"""),
            [
                {
                    "collector": "Merle Dortmond",
                    "trait": "collector",
                    "start": 0,
                    "end": 27,
                },
            ],
        )
