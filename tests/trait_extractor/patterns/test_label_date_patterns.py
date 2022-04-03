"""Test label date unit patterns."""
import unittest
from datetime import date

from dateutil.relativedelta import relativedelta

from tests.setup import test


class TestLabelDate(unittest.TestCase):
    """Test label date patterns."""

    # def test_label_date_00(self):
    #     """It gets a county notation."""
    #     test("""2004 11 05""")

    def test_label_date_01(self):
        """It gets a county notation."""
        self.assertEqual(
            test("""11 May 2004"""),
            [
                {
                    "label_date": "2004-05-11",
                    "trait": "label_date",
                    "start": 0,
                    "end": 11,
                },
            ],
        )

    def test_label_date_02(self):
        """It parses a date with a two digit year."""
        self.assertEqual(
            test("11 may 04"),
            [
                {
                    "label_date": "2004-05-11",
                    "trait": "label_date",
                    "start": 0,
                    "end": 9,
                },
            ],
        )

    def test_label_date_03(self):
        """It adjusts future dates back a century."""
        tomorrow = date.today() + relativedelta(days=1)
        tomorrow = tomorrow.strftime("%d %b %y")
        expect = date.today() + relativedelta(years=-100, days=1)
        expect = expect.strftime("%Y-%m-%d")
        self.assertEqual(
            test(tomorrow),
            [
                {
                    "label_date": expect,
                    "century_adjust": True,
                    "trait": "label_date",
                    "start": 0,
                    "end": 9,
                },
            ],
        )

    def test_label_date_04(self):
        """It handles noise prior to parsing the date."""
        self.assertEqual(
            test("No.: 113,306 Date: 8 October 1989"),
            [
                {
                    "label_date": "1989-10-08",
                    "trait": "label_date",
                    "start": 13,
                    "end": 33,
                },
            ],
        )

    def test_label_date_05(self):
        """It handles an all numeric date."""
        self.assertEqual(
            test("Brent Baker 11-0297 10/20/2011"),
            [
                {
                    "collector_no": "11",
                    "collector": "Brent Baker",
                    "trait": "collector",
                    "start": 0,
                    "end": 14,
                },
                {
                    "label_date": "2011-10-20",
                    "trait": "label_date",
                    "start": 20,
                    "end": 30,
                },
            ],
        )

    def test_label_date_06(self):
        """It handles noise in the separators."""
        self.assertEqual(
            test("Collected by D, M, MOORE — Date AUG-_11,1968"),
            [
                {
                    "label_date": "1968-08-11",
                    "trait": "label_date",
                    "start": 27,
                    "end": 44,
                },
            ],
        )

    def test_label_date_07(self):
        """It handles slashes between the date parts."""
        self.assertEqual(
            test("""Date 8/20/75"""),
            [
                {
                    "label_date": "1975-08-20",
                    "trait": "label_date",
                    "start": 0,
                    "end": 12,
                },
            ],
        )

    def test_label_date_08(self):
        """It handles dates missing a day part (numeric)."""
        self.assertEqual(
            test("Andrew Jenkins 631 2/2010"),
            [
                {
                    "collector_no": "631",
                    "collector": "Andrew Jenkins",
                    "trait": "collector",
                    "start": 0,
                    "end": 18,
                },
                {
                    "label_date": "2010-02",
                    "missing_day": True,
                    "trait": "label_date",
                    "start": 19,
                    "end": 25,
                },
            ],
        )

    def test_label_date_09(self):
        """It does not parse a bad date."""
        self.assertEqual(
            test("Date Oct. 6, 197"),
            [],
        )

    def test_label_date_10(self):
        """It handles a bad month."""
        self.assertEqual(
            test("May have elevation: 1347.22 m (4420 N) - 1359-40 m (4460 Ny"),
            [],
        )

    def test_label_date_11(self):
        """It handles a bad month."""
        self.assertEqual(
            test("June, 1992"),
            [
                {
                    "label_date": "1992-06",
                    "trait": "label_date",
                    "missing_day": True,
                    "start": 0,
                    "end": 10,
                },
            ],
        )
