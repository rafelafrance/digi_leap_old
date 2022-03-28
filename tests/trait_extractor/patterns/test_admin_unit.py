"""Test administrative unit patterns."""
import unittest

from tests.setup import test


class TestAdminUnit(unittest.TestCase):
    """Test administrative unit patterns."""

    def test_admin_unit_01(self):
        """It gets a county notation."""
        self.assertEqual(
            test("""Hempstead County"""),
            [
                {
                    "us_county": "Hempstead",
                    "trait": "admin_unit",
                    "start": 0,
                    "end": 16,
                },
            ],
        )

    def test_admin_unit_02(self):
        """A label is required."""
        self.assertEqual(
            test("""Watauga"""),
            [],
        )

    def test_admin_unit_03(self):
        """It handles a confusing county notation."""
        self.assertEqual(
            test("""Flora of ARKANSAS County: MISSISSIPPI"""),
            [
                {
                    "us_county": "Mississippi",
                    "us_state": "AR",
                    "trait": "admin_unit",
                    "start": 0,
                    "end": 37,
                },
            ],
        )

    def test_admin_unit_04(self):
        """It handles line breaks."""
        self.assertEqual(
            test("""COUNTY:\n\nLee E.L.Nielsen"""),
            [],
        )

    def test_admin_unit_05(self):
        """It handles a trailing county abbreviation."""
        self.assertEqual(
            test("""Alleghany Co,"""),
            [
                {
                    "us_county": "Alleghany",
                    "trait": "admin_unit",
                    "start": 0,
                    "end": 12,
                },
            ],
        )

    def test_admin_unit_06(self):
        """It handles a trailing county abbreviation."""
        self.assertEqual(
            test("""Desha Co., Ark."""),
            [
                {
                    "us_state": "AR",
                    "us_county": "Desha",
                    "trait": "admin_unit",
                    "start": 0,
                    "end": 15,
                }
            ],
        )

    def test_admin_unit_07(self):
        """It works with noisy text."""
        self.assertEqual(
            test(
                """
                Cornus drummondii C. A. Mey.
                Hempstead County
                Grandview Prairie; on CR 35, 10 air miles S/SE of Nashville; in
                """
            ),
            [
                {
                    "us_county": "Hempstead",
                    "trait": "admin_unit",
                    "start": 29,
                    "end": 45,
                },
            ],
        )

    def test_admin_unit_08(self):
        """It gets a state notation."""
        self.assertEqual(
            test("""PLANTS OF ARKANSAS"""),
            [
                {
                    "us_state": "AR",
                    "trait": "admin_unit",
                    "start": 0,
                    "end": 18,
                },
            ],
        )

    def test_admin_unit_09(self):
        """It gets a multi word state notation."""
        self.assertEqual(
            test("""PLANTS OF NORTH CAROLINA"""),
            [
                {
                    "us_state": "NC",
                    "trait": "admin_unit",
                    "start": 0,
                    "end": 24,
                },
            ],
        )

    def test_admin_unit_10(self):
        """It gets a state notation separated from the county."""
        self.assertEqual(
            test(
                """
                APPALACHIAN STATE UNIVERSITY HERBARIUM
                PLANTS OF NORTH CAROLINA
                STONE MOUNTAIN STATE PARK
                WILKES COUNTY
                """
            ),
            [
                {
                    "us_state": "NC",
                    "trait": "admin_unit",
                    "start": 39,
                    "end": 63,
                },
                {
                    "us_county": "Wilkes",
                    "trait": "admin_unit",
                    "start": 90,
                    "end": 103,
                },
            ],
        )

    def test_admin_unit_11(self):
        """It parses multi-word counties and states."""
        self.assertEqual(
            test("""Cape May, New Jersey"""),
            [
                {
                    "us_county": "Cape May",
                    "us_state": "NJ",
                    "trait": "admin_unit",
                    "start": 0,
                    "end": 20,
                },
            ],
        )
