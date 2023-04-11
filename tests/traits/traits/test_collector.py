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
                    "collector": "Christopher Reid & Sarah Nunn",
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
            [{"elevation": 1689.0, "trait": "elevation", "start": 9, "end": 21}],
        )

    def test_collector_13(self):
        self.assertEqual(
            test("""TIMON, R16W,"""),
            [],
        )
