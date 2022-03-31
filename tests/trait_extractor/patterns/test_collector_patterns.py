"""Test collector patterns."""
import unittest

from tests.setup import test


class TestCollector(unittest.TestCase):
    """Test administrative unit patterns."""

    # def test_collector_00(self):
    #     test("""Coll. E. E. Dale Jr. No. 6061""")

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
        """It does not parse other fields."""
        self.assertEqual(
            test(
                """
                Rhus glabra L. "Smooth Sumac"
                Woodruff Co., Arkansas
                Vicinity of bridge on Hwy 33, ca. 2 mi. S. of the
                town of Gregory; S19, T6N; R3W.
                Det, Edwin B. Smith
                Coll. Marie P. Locke No. 5595
                Date June 29, 1985
                """
            ),
            [
                {
                    "collector_no": "5595",
                    "collector": "Marie P. Locke",
                    "trait": "collector",
                    "start": 155,
                    "end": 184,
                },
                {
                    "label_date": "1985-06-29",
                    "trait": "label_date",
                    "start": 185,
                    "end": 203,
                },
                {
                    "us_state": "Arkansas",
                    "us_county": "Woodruff",
                    "trait": "admin_unit",
                    "start": 30,
                    "end": 52,
                },
            ],
        )

    def test_collector_03(self):
        """It handles a bad name."""
        self.assertEqual(
            test(
                """
                APPALACHIAN STATE UNIVERSITY HERBARIUM
                PLANTS OF NORTH CAROLINA
                Collected by _Wayne.. Hutchins.
                """
            ),
            [
                {
                    "collector": "Wayne Hutchins",
                    "trait": "collector",
                    "start": 64,
                    "end": 94,
                },
                {
                    "us_state": "North Carolina",
                    "trait": "admin_unit",
                    "start": 39,
                    "end": 63,
                },
            ],
        )

    def test_collector_04(self):
        """It handles random words matching names."""
        self.assertEqual(
            test(
                """
                Woodsia obtusa (Sprengel) Torrey
                Dry hardwood slope 3 miles south of
                Isothermal Community College.
                Altitude 960 ft.
                Date 6/9/75
                Collected by _Wayne.. Hutchins.
                """
            ),
            [
                {
                    "label_date": "1975-06-09",
                    "trait": "label_date",
                    "start": 116,
                    "end": 127,
                },
                {
                    "collector": "Wayne Hutchins",
                    "trait": "collector",
                    "start": 128,
                    "end": 158,
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
                    "collector": "E. E. Dale Jr.",
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
                    "label_date": "2002-10-20",
                    "trait": "label_date",
                    "start": 34,
                    "end": 49,
                },
            ],
        )

    def test_collector_07(self):
        """It parses collectors separated by '&'."""
        self.assertEqual(
            test(
                """
                Collector: Christopher Reid & Sarah Nunn 2018
                """
            ),
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
