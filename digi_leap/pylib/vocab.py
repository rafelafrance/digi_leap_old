"""Utilities for working with vocabularies."""
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
        db.create_vocab_table(VOCAB_DB)
    return vocab


def in_vocab(vocab, word, min_len=2):
    """Check if the word is in the vocabulary."""
    return re.sub(r"\W", "", word.lower()) in vocab and len(word) > min_len


def is_number(word):
    """Check if the word is a number."""
    # return bool(re.match(r"^ \d+ [.,]? \d* $", word, flags=re.VERBOSE))
    return bool(re.match(r"^ \d+ $", word, flags=re.VERBOSE))


def text_to_words(text):
    """Convert a line of text to words."""
    return re.sub(r"[\W_]+", " ", text.lower()).split()


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
    # words = re.sub(r"[⋄ _-]+", " ", text.lower()).split()
    words = text_to_words(text)
    hits = sum(1 for w in words if in_vocab(ALL_WORDS, w))
    hits += sum(1 for w in words if is_number(w))
    # hits += sum(1 for w in words if is_date(w))
    return hits


ALL_WORDS = get_vocab()
