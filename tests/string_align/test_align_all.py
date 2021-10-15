"""Test the align_all function in the string_align module."""
import unittest

import cppimport.import_hook  # noqa: F401

from digi_leap.pylib import string_align_py as sa
from digi_leap.pylib import string_align_weights as wt


class TestAlignAll(unittest.TestCase):

    two_chars = {"aa": 0.0, "ab": -1.0, "ba": -1.0, "bb": 0.0}

    def test_align_all_01(self):
        self.assertEqual(
            sa.align_all(["aba", "aba"], self.two_chars, -1.0, -1.0), ["aba", "aba"]
        )

    def test_align_all_02(self):
        self.assertEqual(
            sa.align_all(["aba", "aa"], self.two_chars, -1.0, -1.0), ["aba", "a⋄a"]
        )

    def test_align_all_03(self):
        self.assertEqual(
            sa.align_all(["aa", "aba"], self.two_chars, -1.0, -1.0), ["a⋄a", "aba"]
        )

    def test_align_all_04(self):
        self.assertEqual(
            sa.align_all(["aab", "aa"], self.two_chars, -1, -1), ["aab", "aa⋄"]
        )

    def test_align_all_05(self):
        self.assertEqual(
            sa.align_all(["baa", "aa"], self.two_chars, -1, -1), ["baa", "⋄aa"]
        )

    def test_align_all_06(self):
        self.assertEqual(
            sa.align_all(["aa", "baa"], self.two_chars, -1, -1), ["⋄aa", "baa"]
        )

    def test_align_all_07(self):
        self.assertEqual(
            sa.align_all(["aa", "aab"], self.two_chars, -1, -1), ["aa⋄", "aab"]
        )

    def test_align_all_08(self):
        self.assertEqual(
            sa.align_all(["aab", "baa"], self.two_chars, -1, -1), ["aab", "baa"]
        )

    def test_align_all_09(self):
        self.assertEqual(sa.align_all(["aab"], self.two_chars, -1, -1), ["aab"])

    def test_align_all_10(self):
        self.assertRaises(ValueError, sa.align_all, [], self.two_chars, -1, -1)

    def test_align_all_11(self):
        self.assertEqual(
            sa.align_all(["aab", "aaa", "aaa"], self.two_chars, -1, -1),
            ["aab", "aaa", "aaa"],
        )

    def test_align_all_12(self):
        self.assertEqual(
            sa.align_all(["aab", "abb", "aba"], self.two_chars, -1, -1),
            ["aab", "abb", "aba"],
        )

    def test_align_all_13(self):
        self.maxDiff = None
        results = sa.align_all(
            [
                "MOJAVE DESERT, PROVIDENCE MTS.: canyon above",
                "E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above",
                "E MOJAVE DESERT PROVTDENCE MTS. # canyon above",
                "Be ‘MOJAVE DESERT, PROVIDENCE canyon “above",
            ],
            wt.WEIGHTS,
            -5.0,
            -0.5,
        )
        # print()
        # for r in results:
        #    print(f'"{r}",')
        self.assertEqual(
            results,
            [
                "⋄⋄⋄⋄MOJAVE DESERT⋄, PROVIDENCE MTS.⋄⋄: canyon ⋄above",
                "E⋄. MOJAVE DESERT , PROVIDENCE MTS . : canyon ⋄above",
                "E⋄⋄ MOJAVE DESERT ⋄⋄PROVTDENCE MTS. #⋄ canyon ⋄above",
                "Be ‘MOJAVE DESERT⋄, PROVIDENCE ⋄⋄⋄⋄⋄⋄⋄⋄canyon “above",
            ],
            #   "⋄⋄⋄⋄MOJAVE DESERT⋄, PROVIDENCE MTS⋄⋄.: canyon ⋄above",
            #   "E⋄. MOJAVE DESERT , PROVIDENCE MTS . : canyon ⋄above",
            #   "E⋄⋄ MOJAVE DESERT⋄⋄ PROVTDENCE MTS⋄. # canyon ⋄above",
            #   "Be ‘MOJAVE DESERT⋄, PROVIDENCE⋄⋄⋄⋄⋄⋄⋄⋄ canyon “above",
        )
