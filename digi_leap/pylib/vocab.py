"""Utilities for working with vocabularies.

There is plenty of help from: Copyright (c) 2007-2016 Peter Norvig
See http://norvig.com/spell-correct.html
MIT license: www.opensource.org/licenses/mit-license.php
All mistakes are mine.
"""
import string
from sqlite3 import OperationalError

import regex as re

from . import const
from . import db

VOCAB_DB = const.ROOT_DIR / "data" / "vocab.sqlite"


def get_vocab(min_len=3, min_freq=2) -> dict[str, int]:
    """Get a vocabulary used for scoring OCR quality."""
    vocab = {}

    try:
        for row in db.select_vocab(VOCAB_DB):
            word, freq = row["word"], int(row["freq"])

            if len(word) >= min_len and freq >= min_freq:
                vocab[word] = freq

    except OperationalError:
        # Need to create test data to load for testing
        pass
    return vocab


def is_number(word):
    """Check if the word is a number."""
    # return bool(re.match(r"^ \d+ [.,]? \d* $", word, flags=re.VERBOSE))
    return bool(re.match(r"^ \d+ $", word, flags=re.VERBOSE))


def is_date(word):
    """Check if the word is a date."""
    return bool(
        re.match(
            r"^ \d\d? (?P<sep> [/-] ) \d\d? (?P=sep) (\d\d | \d\d\d\d) $",
            word,
            flags=re.VERBOSE,
        )
    )


def vocab_hits(text: str) -> int:
    """Count the number of words in the text that are in our corpus.

    A hit is:
    - A direct match in the vocabularies
    - A number like: 99.99
    """
    words = to_words(text)
    hits = sum(1 for w in words if w in WORDS)
    hits += sum(1 for w in words if is_number(w))
    return hits


WORDS = get_vocab()


# #####################################################################################


def to_words(text):
    """Convert a line of text to words."""
    return re.findall(r"\w+", text.lower())


def prob(word, count=sum(WORDS.values())):
    """Probability of `word`."""
    return WORDS[word] / count


def correction(word):
    """Most probable spelling correction for word."""
    return max(candidates(word), key=prob)


def candidates(word):
    """Generate possible spelling corrections for word."""
    return known([word]) or known(edits1(word)) or known(edits2(word)) or [word]


def known(words_):
    """The subset of `words` that appear in the dictionary of WORDS."""
    return {w for w in words_ if w in WORDS}


def edits1(word):
    """All edits that are one edit away from `word`."""
    letters = string.ascii_lowercase
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    # transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + replaces + inserts)  # + transposes)


def edits2(word):
    """All edits that are two edits away from `word`."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
