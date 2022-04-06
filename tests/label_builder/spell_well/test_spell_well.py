"""Test the spell checker."""
import unittest

from digi_leap.pylib.label_builder.spell_well.spell_well import SpellWell


class TestSpellWell(unittest.TestCase):
    spell_well = SpellWell(vocab_db="tests/mock_data/vocab.sqlite")

    def test_correct_01(self):
        self.assertEqual(self.spell_well.correct("Missing"), "Missing")

    def test_correct_02(self):
        self.assertEqual(self.spell_well.correct(None), "")

    def test_correct_03(self):
        self.assertEqual(self.spell_well.correct("abdome"), "abdomen")

    def test_correct_04(self):
        self.assertEqual(self.spell_well.correct("abdoman"), "abdomen")
