"""Test the levenshtein function in the line_align module."""
import unittest

import cppimport.import_hook  # noqa: F401

from digi_leap.pylib.label_builder.line_align import line_align_py as line_align


class TestDistance(unittest.TestCase):
    def setUp(self):
        self.la = line_align.LineAlign()

    def test_distance_01(self):
        self.assertEqual(self.la.levenshtein("aa", "bb"), 2)

    def test_distance_02(self):
        self.assertEqual(self.la.levenshtein("ab", "bb"), 1)

    def test_distance_03(self):
        self.assertEqual(self.la.levenshtein("ab", "ab"), 0)

    def test_distance_04(self):
        self.assertEqual(self.la.levenshtein("aa", "aba"), 1)

    def test_distance_05(self):
        self.assertEqual(self.la.levenshtein("aa", "baa"), 1)

    def test_distance_06(self):
        self.assertEqual(self.la.levenshtein("aa", "aab"), 1)

    def test_distance_07(self):
        self.assertEqual(self.la.levenshtein("baa", "aa"), 1)

    def test_distance_08(self):
        self.assertEqual(self.la.levenshtein("aab", "aa"), 1)

    def test_distance_09(self):
        self.assertEqual(self.la.levenshtein("baab", "aa"), 2)

    def test_distance_10(self):
        self.assertEqual(self.la.levenshtein("aa", "baab"), 2)

    def test_distance_11(self):
        self.assertEqual(self.la.levenshtein("", "aa"), 2)

    def test_distance_12(self):
        self.assertEqual(self.la.levenshtein("aa", ""), 2)

    def test_distance_13(self):
        self.assertEqual(self.la.levenshtein("", ""), 0)

    def test_distance_14(self):
        self.assertEqual(1, self.la.levenshtein("aa", "五aa"))

    def test_distance_15(self):
        self.assertEqual(1, self.la.levenshtein("五aa", "aa"))

    def test_distance_16(self):
        self.assertEqual(1, self.la.levenshtein("aa", "aa五"))

    def test_distance_17(self):
        self.assertEqual(1, self.la.levenshtein("aa五", "aa"))

    def test_distance_18(self):
        self.assertEqual(1, self.la.levenshtein("a五a", "aa"))

    def test_distance_19(self):
        self.assertEqual(1, self.la.levenshtein("aa", "a五a"))

    def test_distance_20(self):
        self.assertEqual(1, self.la.levenshtein("五五", "五六"))

    def test_distance_21(self):
        self.assertEqual(0, self.la.levenshtein("五五", "五五"))
