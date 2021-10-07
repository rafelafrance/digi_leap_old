"""Test the distance function in the string_align module."""

import unittest

import digi_leap.pylib.string_align as sa


class TestAlignAll(unittest.TestCase):

    def test_align_01(self):
        self.assertEqual(sa.align("aba", "aba"), [(0, "aba", "aba")])

    def test_align_02(self):
        self.assertEqual(sa.align("aba", "aa"), [(1, "aba", "a-a")])

    def test_align_03(self):
        self.assertEqual(sa.align("aa", "aba"), [(1, "a-a", "aba")])

    def test_align_04(self):
        self.assertEqual(sa.align("aab", "aa"), [(1, "aab", "aa-")])

    def test_align_05(self):
        self.assertEqual(sa.align("baa", "aa"), [(1, "baa", "-aa")])

    def test_align_06(self):
        self.assertEqual(sa.align("aa", "baa"), [(1, "-aa", "baa")])

    def test_align_07(self):
        self.assertEqual(sa.align("aa", "aab"), [(1, "aa-", "aab")])

    def test_align_08(self):
        self.assertEqual(
            sa.align("aab", "baa"),
            [(2, "aab", "baa"), (2, "-aab", "baa-")])
