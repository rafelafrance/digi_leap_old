"""Test the distance function in the levenshtein module."""

import unittest

import cppimport.import_hook
import digi_leap.pylib.levenshtein as lev


class TestDistanceAll(unittest.TestCase):

    def test_distance_all_01(self):
        self.assertEqual(lev.distance_all(["aa", "bb"]), [(0, 1, 2)])

    def test_distance_all_02(self):
        self.assertEqual(
            lev.distance_all(["aa", "bb", "ab"]),
            [(0, 2, 1), (1, 2, 1), (0, 1, 2)])
