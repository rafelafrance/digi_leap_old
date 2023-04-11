import unittest

from tests.setup import test


class TestAssociatedTaxon(unittest.TestCase):
    def test_associated_taxon_01(self):
        """It labels a primary and associated taxa."""
        self.assertEqual(
            test(
                """
                Cephalanthus occidentalis L. Rubiaceas
                Associated species: Cornus obliqua
                """
            ),
            [
                {
                    "taxon": "Cephalanthus occidentalis",
                    "rank": "species",
                    "authority": "L. Rubiaceas",
                    "trait": "taxon",
                    "start": 0,
                    "end": 38,
                    "primary": "primary",
                },
                {
                    "taxon": "Cornus obliqua",
                    "rank": "species",
                    "trait": "taxon",
                    "start": 59,
                    "end": 73,
                    "primary": "associated",
                },
            ],
        )

    def test_associated_taxon_02(self):
        """It does not label the first taxon after the label."""
        self.assertEqual(
            test(""""Associated species: Cornus obliqua"""),
            [
                {
                    "taxon": "Cornus obliqua",
                    "rank": "species",
                    "trait": "taxon",
                    "start": 21,
                    "end": 35,
                    "primary": "associated",
                }
            ],
        )

    def test_associated_taxon_03(self):
        """It does not label a higher taxon as primary."""
        self.assertEqual(
            test(
                """
                Fabaceae
                Cephalanthus occidentalis L. Rubiaceas
                Associated species: Cornus obliqua
                """
            ),
            [
                {
                    "taxon": "Fabaceae",
                    "rank": "family",
                    "trait": "taxon",
                    "start": 0,
                    "end": 8,
                    "primary": "associated",
                },
                {
                    "taxon": "Cephalanthus occidentalis",
                    "rank": "species",
                    "authority": "L. Rubiaceas",
                    "trait": "taxon",
                    "start": 9,
                    "end": 47,
                    "primary": "primary",
                },
                {
                    "taxon": "Cornus obliqua",
                    "rank": "species",
                    "trait": "taxon",
                    "start": 68,
                    "end": 82,
                    "primary": "associated",
                },
            ],
        )
