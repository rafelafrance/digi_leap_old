"""Test the distance function in the levenshtein module."""

import unittest

import cppimport.import_hook
from digi_leap.pylib import levenshtein as lev


class TestDistance(unittest.TestCase):

    def test_distance_01(self):
        self.assertEqual(lev.distance("aa", "bb"), 2)

    def test_distance_02(self):
        self.assertEqual(lev.distance("ab", "bb"), 1)

    def test_distance_03(self):
        self.assertEqual(lev.distance("ab", "ab"), 0)

    def test_distance_04(self):
        self.assertEqual(lev.distance("aa", "aba"), 1)

    def test_distance_05(self):
        self.assertEqual(lev.distance("aa", "baa"), 1)

    def test_distance_06(self):
        self.assertEqual(lev.distance("aa", "aab"), 1)

    def test_distance_07(self):
        self.assertEqual(lev.distance("baa", "aa"), 1)

    def test_distance_08(self):
        self.assertEqual(lev.distance("aab", "aa"), 1)

    def test_distance_09(self):
        self.assertEqual(lev.distance("baab", "aa"), 2)

    def test_distance_10(self):
        self.assertEqual(lev.distance("aa", "baab"), 2)

    def test_distance_11(self):
        self.assertEqual(lev.distance("", "aa"), 2)

    def test_distance_12(self):
        self.assertEqual(lev.distance("aa", ""), 2)

    def test_distance_13(self):
        self.assertEqual(lev.distance("", ""), 0)

    def test_distance_14(self):
        self.assertEqual(1, lev.distance("aa", "五aa"))

    def test_distance_15(self):
        self.assertEqual(1, lev.distance("五aa", "aa"))

    def test_distance_16(self):
        self.assertEqual(1, lev.distance("aa", "aa五"))

    def test_distance_17(self):
        self.assertEqual(1, lev.distance("aa五", "aa"))

    def test_distance_18(self):
        self.assertEqual(1, lev.distance("a五a", "aa"))

    def test_distance_19(self):
        self.assertEqual(1, lev.distance("aa", "a五a"))

    def test_distance_20(self):
        self.assertEqual(1, lev.distance("五五", "五六"))

    def test_distance_21(self):
        self.assertEqual(0, lev.distance("五五", "五五"))
