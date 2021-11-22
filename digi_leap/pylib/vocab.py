"""Utilities for working with vocabularies.

Modified from: Copyright (c) 2007-2016 Peter Norvig
See http://norvig.com/spell-correct.html
MIT license: www.opensource.org/licenses/mit-license.php
"""
import logging
import sqlite3
import string
from typing import Iterable

import regex as re

from . import const
from . import db

VOCAB_DB = const.ROOT_DIR / "data" / "vocab.sqlite"

LETTERS = string.ascii_lowercase + "ªµºßàáâãäåæçèéêëìíîïðñóôõöøùúûüýčěšū"


def get_vocab(min_freq=5, min_len=3) -> dict[str, float]:
    """Get a vocabulary used for scoring OCR quality."""
    vocab = {}

    try:
        for row in db.select_vocab(VOCAB_DB, min_freq, min_len):
            vocab[row["word"]] = row["freq"]
    except sqlite3.OperationalError as e:
        logging.error(e)

    return vocab


WORDS = get_vocab()


def is_date(word):
    """Check if the word is a date."""
    return bool(
        re.match(
            r"^ \d\d? (?P<sep> [/-] ) \d\d? (?P=sep) (\d\d | \d\d\d\d) $",
            word,
            flags=re.VERBOSE,
        )
    )


def number_split(text: str) -> list[str]:
    """Split the text into numbers and non-numbers."""
    return re.split(r"([^\d]+)", text)


def is_number(word):
    """Check if the word is a number."""
    # return bool(re.match(r"^ \d+ [.,]? \d* $", word, flags=re.VERBOSE))
    return bool(re.match(r"^ \d+ $", word, flags=re.VERBOSE))


def tokenize(text: str) -> list[str]:
    """Split the text into words and non-words."""
    return re.split(r"([^\p{L}]+)", text)


def is_word(word: str) -> bool:
    """Determine if this is a word or a separator after tokenize()."""
    return word.lower() in WORDS


def hits(text: str) -> int:
    """Count the number of words in the text that are in our corpus.

    A hit is:
    - A direct match in the vocabularies
    - A number like: 99.99
    """
    count = sum(1 for w in tokenize(text) if is_word(w))
    count += sum(1 for w in number_split(text) if is_number(w))
    return count


# #####################################################################################


def usage(word):
    """Get the number of times 'word' appears in the corpus."""
    return WORDS.get(word.lower(), 0)


def prob(word: str, count: float = sum(WORDS.values())) -> float:
    """Probability of 'word'."""
    return usage(word) / count


def spell_correct(word: str) -> str:
    """Most probable spelling for 'word'."""
    if not word:
        return ""

    best = max(candidates(word), key=usage)

    # Handle the case of the 'word'
    if word[0].isupper():
        best = best.upper() if word[-1].isupper() else best.title()

    return best


def candidates(word: str) -> set:
    """Generate possible spelling corrections for 'word'."""
    word = word.lower()
    return known([word]) or known(edits1(word)) or known(edits2(word)) or {word}


def known(words: Iterable) -> set:
    """The subset of 'words' that appear in the dictionary of WORDS."""
    return {w for w in words if w in WORDS}


def edits1(word: str) -> set:
    """All edits that are one edit away from 'word'."""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    inserts = [L + c + R for L, R in splits for c in LETTERS]
    replaces = [L + c + R[1:] for L, R in splits if R for c in LETTERS]
    # transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    return set(deletes + inserts + replaces)  # + transposes)


def edits2(word: str):
    """All edits that are two edits away from 'word'."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
