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
                },
                {
                    "associated_taxon": "Cornus obliqua",
                    "rank": "species",
                    "trait": "associated_taxon",
                    "start": 59,
                    "end": 73,
                },
            ],
        )

    def test_associated_taxon_02(self):
        """It does not label the first taxon after the label."""
        self.assertEqual(
            test("""Associated species: Cornus obliqua"""),
            [
                {
                    "associated_taxon": "Cornus obliqua",
                    "rank": "species",
                    "trait": "associated_taxon",
                    "start": 20,
                    "end": 34,
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
                    "associated_taxon": "Fabaceae",
                    "rank": "family",
                    "trait": "associated_taxon",
                    "start": 0,
                    "end": 8,
                },
                {
                    "taxon": "Cephalanthus occidentalis",
                    "rank": "species",
                    "authority": "L. Rubiaceas",
                    "trait": "taxon",
                    "start": 9,
                    "end": 47,
                },
                {
                    "associated_taxon": "Cornus obliqua",
                    "rank": "species",
                    "trait": "associated_taxon",
                    "start": 68,
                    "end": 82,
                },
            ],
        )

    def test_associated_taxon_04(self):
        """It does not label the first taxon after the label."""
        self.assertEqual(
            test(""" Cornus obliqua near Cephalanthus occidentalis """),
            [
                {
                    "taxon": "Cornus obliqua",
                    "rank": "species",
                    "trait": "taxon",
                    "start": 0,
                    "end": 14,
                },
                {
                    "associated_taxon": "Cephalanthus occidentalis",
                    "rank": "species",
                    "trait": "associated_taxon",
                    "start": 20,
                    "end": 45,
                },
            ],
        )
