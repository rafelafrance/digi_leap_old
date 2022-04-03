"""Test taxon patterns."""
import unittest

from tests.setup import test


class TestTaxon(unittest.TestCase):
    """Test taxon patterns."""

    # def test_taxon_00(self):
    #     test("""Fabaceae Vicia villosa Roth ssp. varia (Host) Corb. CLAY COUNTY""")

    def test_taxon_01(self):
        """It gets a taxon notation."""
        self.assertEqual(
            test(
                """
                Cornaceae
                Cornus obliqua Raf.
                Washington County
                """
            ),
            [
                {
                    "family": "Cornaceae",
                    "genus": "Cornus",
                    "species": "obliqua",
                    "authority": "Raf",
                    "trait": "taxon",
                    "start": 0,
                    "end": 28,
                },
                {
                    "us_county": "Washington",
                    "trait": "admin_unit",
                    "start": 30,
                    "end": 47,
                },
            ],
        )

    def test_taxon_02(self):
        """It gets a family notation."""
        self.assertEqual(
            test(
                """
                Crowley's Ridge
                Fabaceae
                Vicia villosa Roth ssp. varia (Host) Corb.
                CLAY COUNTY
                """
            ),
            [
                {
                    "family": "Fabaceae",
                    "genus": "Vicia",
                    "species": "villosa",
                    "subspecies": "varia",
                    "authority": "Roth",
                    "trait": "taxon",
                    "start": 16,
                    "end": 54,
                },
                {"us_county": "Clay", "trait": "admin_unit", "start": 68, "end": 79},
            ],
        )

    def test_taxon_03(self):
        """It gets the full notation."""
        self.assertEqual(
            test("""Cephalanthus occidentalis L. Rubiaceas"""),
            [
                {
                    "genus": "Cephalanthus",
                    "species": "occidentalis",
                    "authority": "L. Rubiaceas",
                    "trait": "taxon",
                    "start": 0,
                    "end": 38,
                }
            ],
        )
