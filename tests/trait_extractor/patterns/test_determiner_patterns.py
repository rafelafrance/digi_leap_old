"""Test determiner patterns."""
import unittest

from tests.setup import test


class TestCollector(unittest.TestCase):

    # def test_collector_00(self):
    #     test("""Coll. E. E. Dale Jr. No. 6061""")

    def test_determiner_01(self):
        """It gets a multiple name notations."""
        self.assertEqual(
            test("""Det;; N. H Russell 195"""),
            [
                {
                    "determiner_no": "195",
                    "determiner": "N. H Russell",
                    "trait": "determiner",
                    "start": 0,
                    "end": 22,
                }
            ],
        )
