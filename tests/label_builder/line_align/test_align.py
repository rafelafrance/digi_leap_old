"""Test the align function in the line_align module."""
import unittest

import cppimport.import_hook  # noqa pylint: disable=unused-import

from digi_leap.pylib.label_builder.line_align import line_align_py  # noqa
from digi_leap.pylib.label_builder.line_align import line_align_subs as subs


class TestAlign(unittest.TestCase):
    def setUp(self):
        two_chars = {"aa": 0.0, "ab": -1.0, "bb": 0.0}
        self.line = line_align_py.LineAlign(two_chars, -1.0, -1.0)

    def test_align_01(self):
        self.assertEqual(self.line.align(["aba", "aba"]), ["aba", "aba"])

    def test_align_02(self):
        self.assertEqual(self.line.align(["aba", "aa"]), ["aba", "a⋄a"])

    def test_align_03(self):
        self.assertEqual(self.line.align(["aa", "aba"]), ["a⋄a", "aba"])

    def test_align_04(self):
        self.assertEqual(self.line.align(["aab", "aa"]), ["aab", "aa⋄"])

    def test_align_05(self):
        self.assertEqual(self.line.align(["baa", "aa"]), ["baa", "⋄aa"])

    def test_align_06(self):
        self.assertEqual(self.line.align(["aa", "baa"]), ["⋄aa", "baa"])

    def test_align_07(self):
        self.assertEqual(self.line.align(["aa", "aab"]), ["aa⋄", "aab"])

    def test_align_08(self):
        self.assertEqual(self.line.align(["aab", "baa"]), ["aab", "baa"])

    def test_align_09(self):
        self.assertEqual(self.line.align(["aab"]), ["aab"])

    def test_align_10(self):
        self.assertEqual(self.line.align([]), [])

    def test_align_11(self):
        self.assertEqual(self.line.align(["aab", "aaa", "aaa"]), ["aab", "aaa", "aaa"])

    def test_align_12(self):
        self.assertEqual(self.line.align(["aab", "abb", "aba"]), ["aab", "abb", "aba"])

    def test_align_13(self):
        line = line_align_py.LineAlign(substitutions=subs.SUBS, gap=-3.0)
        results = line.align(
            [
                "MOJAVE DESERT, PROVIDENCE MTS.: canyon above",
                "E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above",
                "E MOJAVE DESERT PROVTDENCE MTS. # canyon above",
                "Be ‘MOJAVE DESERT, PROVIDENCE canyon “above",
            ],
        )
        # print()
        # for r in results:
        #     print(f'"{r}",')
        self.assertEqual(
            results,
            [
                "⋄⋄⋄⋄MOJAVE DESERT⋄, PROVIDENCE MTS.⋄⋄: canyon ⋄above",
                "E⋄. MOJAVE DESERT , PROVIDENCE MTS . : canyon ⋄above",
                "E⋄⋄ MOJAVE DESERT ⋄⋄PROVTDENCE MTS. #⋄ canyon ⋄above",
                "Be ‘MOJAVE DESERT⋄, PROVIDENCE ⋄⋄⋄⋄⋄⋄⋄⋄canyon “above",
            ],
        )

    def test_align_14(self):
        line = line_align_py.LineAlign(subs.SUBS)
        results = line.align(
            [
                "Johns Island Sta tion on",
                " Johns Island Stati on on",
                "Johns Island Station on i",
                "Station or",
            ],
        )
        # print()
        # for r in results:
        #     print(f'"{r}",')
        self.assertEqual(
            results,
            [
                "⋄Johns Island Sta ti⋄on on⋄⋄",
                " Johns Island Sta⋄ti on on⋄⋄",
                "⋄Johns Island Sta⋄ti⋄on on i",
                "⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄⋄Sta⋄ti⋄on or⋄⋄",
            ],
        )
