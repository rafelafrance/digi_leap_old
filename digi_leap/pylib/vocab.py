"""Utilities for working with vocabularies."""
import re
from typing import Optional

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


def text_hits(text: str, vocab: Optional[set] = None) -> int:
    """Count the number of words in the text that are in our corpus.

    A hit is:
    - A direct match in the vocabulary
    - A number like: 99.99
    - A data like: 1/22/34 or 11-2-34
    """
    words = text.lower().split()
    hits = sum(1 for w in words if re.sub(r"\W", "", w) in VOCAB and len(w) > 2)
    hits += sum(1 for w in words if re.match(r"^\d+[.,]?\d*$", w))
    hits += sum(1 for w in words if re.match(r"^\d\d?[/-]\d\d?[/-]\d\d$", w))
    return hits
