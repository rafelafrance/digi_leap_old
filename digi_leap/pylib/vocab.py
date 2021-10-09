"""Utilities for working with vocabularies."""
import nltk

from . import const

VOCAB_DIR = const.ROOT_DIR / "vocab"


# Vocabulary for scoring OCR quality
def get_vocab() -> set[str]:
    """Get the vocabulary used for scoring OCR quality."""
    vocab = set()
    with open(VOCAB_DIR / "plant_taxa.txt") as in_file:
        vocab |= {v.strip().lower() for v in in_file.readlines() if len(v) > 1}
    vocab |= {w.lower() for w in nltk.corpus.words.words() if len(w) > 1}
    return vocab


VOCAB = get_vocab()
