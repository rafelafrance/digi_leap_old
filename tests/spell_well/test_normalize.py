"""Test the SpellWell.normalize() function."""
import string
import unittest

import cppimport.import_hook  # noqa: F401

from digi_leap.pylib import spell_well_py as sw


class TestNormalize(unittest.TestCase):
    def setUp(self):
        vocab = {"ää": 1, "bb": 2, "cc": 3}
        lowers = string.ascii_lowercase
        self.sw = sw.SpellWell(vocab, lowers)

    # def test_normalize_01(self):
    #     self.assertEqual(self.sw.normalize("ÄB"), "äb")
