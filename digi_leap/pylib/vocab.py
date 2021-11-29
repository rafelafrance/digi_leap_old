"""Utilities for working with vocabularies.

Based off of symmetric deletes method from SeekStorm. MIT license.
https://seekstorm.com/blog/1000x-spelling-correction/
"""
import logging
import sqlite3
from collections import namedtuple
from typing import Iterable

import regex as re

from . import const
from . import db

VOCAB_DB = const.ROOT_DIR / "data" / "vocab.sqlite"

Spell = namedtuple("Spell", "word dist freq")


class SpellWell:
    """A simple spell checker."""

    null_spell = Spell("", 99, -1.0)

    def __init__(self, min_freq=5, min_len=3):
        self.min_len = min_len
        self.min_freq = min_freq

        self.spell = {}
        try:
            for row in db.select_misspellings(VOCAB_DB, min_freq, min_len):
                self.spell[row["miss"]] = Spell(row["word"], row["dist"], row["freq"])
        except sqlite3.OperationalError as e:
            logging.error(e)

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Split the text into words and non-words."""
        return re.split(r"([^\p{L}]+)", text)

    def is_word(self, word: str) -> bool:
        """Determine if this is a word or a separator after tokenize()."""
        spell = self.spell.get(word, self.null_spell)
        return spell.dist == 0

    def hits(self, text: str) -> int:
        """Count the number of words in the text that are in our corpus.

        A hit is:
        - A direct match in the vocabularies
        - A number like: 99.99
        """
        count = sum(1 for w in self.tokenize(text) if self.is_word(w))
        count += sum(1 for _ in re.findall(r"\d+", text))
        return count

    @staticmethod
    def deletes1(word: str) -> set[str]:
        """Generate all one character deletes for a word."""
        return {word[:i] + word[i + 1 :] for i in range(len(word))}

    def deletes2(self, word: str) -> set[str]:
        """Generate two character deletes for a word."""
        return {d2 for d1 in self.deletes1(word) for d2 in self.deletes1(d1)}

    def spell_correct(self, word: str) -> str:
        """Most probable spelling for 'word'."""
        word = word if word else ""

        best = max(self.candidates(word), key=lambda w: w.freq)

        return best.word

    def known(self, words: Iterable) -> set:
        """The subset of 'words' that appear in the dictionary of misspellings."""
        return {w for w in words if w in self.spell}

    def candidates(self, word: str) -> set:
        """Generate possible spelling corrections for 'word'."""
        return (
            self.known([word])
            or self.known(self.deletes1(word))
            or self.known(self.deletes2(word))
            or {word}
        )
