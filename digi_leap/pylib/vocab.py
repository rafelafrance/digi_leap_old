"""Utilities for working with vocabularies."""
from functools import reduce
from sys import intern

import nltk
import regex as re

from . import const

VOCAB_DIR = const.ROOT_DIR / "vocab"


def get_word_set(words_list, min_len=2) -> set[str]:
    """Get a vocabulary used for scoring OCR quality."""
    with open(words_list) as in_file:
        vocab = {
            intern(v.strip().lower()) for v in in_file.readlines() if len(v) > min_len
        }
    return vocab


def get_nltk_vocab(min_len=2) -> set[str]:
    """Get common words from NLTK."""
    vocab = {intern(w.lower()) for w in nltk.corpus.words.words() if len(w) > min_len}
    vocab -= {"wes", "stof"}
    return vocab


def in_vocab(vocab, word, min_len=2):
    """Check if the word is in the vocabulary."""
    return intern(re.sub(r"\W", "", word.lower())) in vocab and len(word) > min_len


def is_number(word):
    """Check if the word is a number."""
    return bool(re.match(r"^ \d+ [.,]? \d* $", word, flags=re.VERBOSE))


def is_date(word):
    """Check if the word is a date."""
    return bool(
        re.match(
            r"^ \d\d? (?P<sep> [/-] ) \d\d? (?P=sep) (\d\d | \d\d\d\d) $",
            word,
            flags=re.VERBOSE,
        )
    )


VOCAB: dict[str, set] = {
    "plant_taxa": get_word_set(VOCAB_DIR / "plant_taxa.txt"),
    "common": get_nltk_vocab(),
}
ALL_WORDS: set = reduce(lambda x, y: x.union(y), VOCAB.values(), set())


def in_any_vocab(word, min_len=2):
    """Check if a word is in any vocabulary."""
    word = word.lower()
    return len(word) > min_len and (
        in_vocab(ALL_WORDS, word) or is_number(word) or is_date(word)
    )


def vocab_hits(text: str) -> int:
    """Count the number of words in the text that are in our corpus.

    A hit is:
    - A direct match in the vocabularies
    - A number like: 99.99
    - A data like: 1/22/34 or 11-2-1934
    """
    words = text.split()
    hits = sum(1 for w in words if in_vocab(ALL_WORDS, w))
    hits += sum(1 for w in words if is_number(w))
    hits += sum(1 for w in words if is_date(w))
    return hits
