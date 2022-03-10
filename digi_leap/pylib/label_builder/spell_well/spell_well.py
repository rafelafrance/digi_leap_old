"""Utilities for working with vocabularies.

Based off of symmetric deletes method from SeekStorm. MIT license.
https://seekstorm.com/blog/1000x-spelling-correction/
"""
import logging
import sqlite3
from collections import namedtuple
from typing import Iterable

import regex as re

from digi_leap.pylib import consts

VOCAB_DB = consts.ROOT_DIR / "data" / "vocab.sqlite"

Spell = namedtuple("Spell", "word dist freq")


class SpellWell:
    """A simple spell checker."""

    null_spell = Spell("", 99, -1.0)

    def __init__(self, min_freq=5, min_len=3, vocab_db=VOCAB_DB):
        self.min_len = min_len
        self.min_freq = min_freq
        self.vocab_db = vocab_db
        self.cxn = sqlite3.connect(":memory:")
        self.db_to_memory()

    def db_to_memory(self):
        """Move the misspellings table to memory."""
        create = """
            create table spells as
            select * from aux.misspellings where freq >= ? and length(miss) >= ?;"""
        index = """create index spells_miss on spells (miss);"""
        try:
            self.cxn.execute(f"attach database '{self.vocab_db}' as aux")
            self.cxn.execute(create, (self.min_freq, self.min_len))
            self.cxn.execute(index)
            self.cxn.execute("detach database aux")
        except sqlite3.OperationalError as e:
            logging.error(e)

    def correct(self, word: str) -> str:
        """Most probable spelling for 'word'."""
        if not word:
            return ""

        if hit := (self.best([word], 0) or self.best([word], 1)):
            return hit

        all_deletes = self.deletes1(word) | self.deletes2(word)

        if hit := self.best(all_deletes, 1):
            return hit

        return word

    def best(self, words: Iterable, dist: int) -> str:
        """The subset of 'words' that appear in the dictionary of misspellings."""
        words = ",".join({f"'{w}'" for w in words})
        sql = f"""select word, dist, freq
                    from spells
                   where miss in ({words})
                     and dist <= ?
                order by freq desc"""
        hit = self.cxn.execute(sql, (dist,)).fetchone()
        return hit[0] if hit else ""

    @staticmethod
    def deletes1(word: str) -> set[str]:
        """Generate all one character deletes for a word."""
        return {word[:i] + word[i + 1 :] for i in range(len(word))}

    def deletes2(self, word: str) -> set[str]:
        """Generate two character deletes for a word."""
        return {d2 for d1 in self.deletes1(word) for d2 in self.deletes1(d1)}

    @staticmethod
    def is_letters(text: str) -> list[str]:
        """Split the text into words and non-words."""
        return re.match(r"^\p{L}+$", text)

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Split the text into words and non-words."""
        return re.split(r"([^\p{L}]+)", text)

    def is_word(self, word: str) -> bool:
        """Determine if this is a word ."""
        sql = "select word from spells where miss = ? and dist = 0"
        hit = self.cxn.execute(sql, (word,)).fetchone()
        return bool(hit)

    def hits(self, text: str) -> int:
        """Count the number of words in the text that are in our corpus.

        A hit is:
        - A direct match in the vocabularies
        - A number like: 99.99
        """
        count = sum(1 for w in self.tokenize(text) if self.is_word(w))
        count += sum(1 for _ in re.findall(r"\d+", text))
        return count
