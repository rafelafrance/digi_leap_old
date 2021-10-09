"""Test the distance function in the string_align module."""
import unittest

from digi_leap.pylib import string_align as sa


class TestDistanceAll(unittest.TestCase):
    def test_distance_all_01(self):
        self.assertEqual(sa.levenshtein_all(["aa", "bb"]), [(2, 0, 1)])

    def test_distance_all_02(self):
        self.assertEqual(
            sa.levenshtein_all(["aa", "bb", "ab"]), [(1, 0, 2), (1, 1, 2), (2, 0, 1)]
        )
