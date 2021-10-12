"""Test the align function in the string_align module."""
import unittest

import digi_leap.pylib.string_align as sa


class TestAlign(unittest.TestCase):
    def test_align_01(self):
        self.assertEqual(sa.align(["aba", "aba"]), ["aba", "aba"])

    def test_align_02(self):
        self.assertEqual(sa.align(["aba", "aa"]), ["aba", "a⋄a"])

    def test_align_03(self):
        self.assertEqual(sa.align(["aa", "aba"]), ["a⋄a", "aba"])

    def test_align_04(self):
        self.assertEqual(sa.align(["aab", "aa"]), ["aab", "aa⋄"])

    def test_align_05(self):
        self.assertEqual(sa.align(["baa", "aa"]), ["baa", "⋄aa"])

    def test_align_06(self):
        self.assertEqual(sa.align(["aa", "baa"]), ["⋄aa", "baa"])

    def test_align_07(self):
        self.assertEqual(sa.align(["aa", "aab"]), ["aa⋄", "aab"])

    def test_align_08(self):
        self.assertEqual(sa.align(["aab", "baa"]), ["aab", "baa"])

    def test_align_09(self):
        self.assertEqual(sa.align(["aab"]), ["aab"])

    def test_align_10(self):
        self.assertRaises(ValueError, sa.align, [])
