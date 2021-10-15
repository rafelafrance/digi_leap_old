"""Test the levenshtein function in the string_align module."""
import unittest

import cppimport.import_hook  # noqa: F401

from digi_leap.pylib import string_align_py as sa


class TestDistance(unittest.TestCase):
    def test_distance_01(self):
        self.assertEqual(sa.levenshtein("aa", "bb"), 2)

    def test_distance_02(self):
        self.assertEqual(sa.levenshtein("ab", "bb"), 1)

    def test_distance_03(self):
        self.assertEqual(sa.levenshtein("ab", "ab"), 0)

    def test_distance_04(self):
        self.assertEqual(sa.levenshtein("aa", "aba"), 1)

    def test_distance_05(self):
        self.assertEqual(sa.levenshtein("aa", "baa"), 1)

    def test_distance_06(self):
        self.assertEqual(sa.levenshtein("aa", "aab"), 1)

    def test_distance_07(self):
        self.assertEqual(sa.levenshtein("baa", "aa"), 1)

    def test_distance_08(self):
        self.assertEqual(sa.levenshtein("aab", "aa"), 1)

    def test_distance_09(self):
        self.assertEqual(sa.levenshtein("baab", "aa"), 2)

    def test_distance_10(self):
        self.assertEqual(sa.levenshtein("aa", "baab"), 2)

    def test_distance_11(self):
        self.assertEqual(sa.levenshtein("", "aa"), 2)

    def test_distance_12(self):
        self.assertEqual(sa.levenshtein("aa", ""), 2)

    def test_distance_13(self):
        self.assertEqual(sa.levenshtein("", ""), 0)

    def test_distance_14(self):
        self.assertEqual(1, sa.levenshtein("aa", "五aa"))

    def test_distance_15(self):
        self.assertEqual(1, sa.levenshtein("五aa", "aa"))

    def test_distance_16(self):
        self.assertEqual(1, sa.levenshtein("aa", "aa五"))

    def test_distance_17(self):
        self.assertEqual(1, sa.levenshtein("aa五", "aa"))

    def test_distance_18(self):
        self.assertEqual(1, sa.levenshtein("a五a", "aa"))

    def test_distance_19(self):
        self.assertEqual(1, sa.levenshtein("aa", "a五a"))

    def test_distance_20(self):
        self.assertEqual(1, sa.levenshtein("五五", "五六"))

    def test_distance_21(self):
        self.assertEqual(0, sa.levenshtein("五五", "五五"))
