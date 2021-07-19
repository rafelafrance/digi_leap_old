"""Define literals used in the system."""

import os
from pathlib import Path

import numpy as np
import nltk
from nltk.corpus import words

BATCH_SIZE = 1_000_000  # How many records to work with at a time

ROOT_DIR = Path(".." if os.getcwd().endswith("scratch") else ".")
DATA_DIR = ROOT_DIR / "data"

IMAGE_DIR = DATA_DIR / "images"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DIR = DATA_DIR / "raw"
TEMP_DIR = DATA_DIR / "temp"
VOCAB_DIR = DATA_DIR / "vocab"
FONTS_DIR = ROOT_DIR / "fonts"

CSV_FILE = "occurrence_raw.csv"
DB = PROCESSED_DIR / "occurrence_raw_2021-02.sqlite3.db"

CHAR_BLACKLIST = "¥€£¢$«»®©§{}[]<>|"
TESS_CONFIG = " ".join(
    [
        "-l eng",
        f"-c tessedit_char_blacklist='{CHAR_BLACKLIST}'",
    ]
)
TESS_LANG = "eng"

HORIZ_ANGLES = np.array([0.0, 0.5, -0.5, 1.0, -1.0, 1.5, -1.5, 2.0, -2.0])
NEAR_HORIZ = np.deg2rad(HORIZ_ANGLES)
NEAR_VERT = np.deg2rad(np.linspace(88.0, 92.0, num=9))
NEAR_HORIZ, NEAR_VERT = NEAR_VERT, NEAR_HORIZ  # ?!


def get_nltk_words():
    """Get words from the NLTK corpus."""
    nltk.download("words")


def get_vocab() -> set[str]:
    """Get the vocabulary used for scoring OCR quality."""
    vocab = set()

    with open(VOCAB_DIR / "plant_taxa.txt") as in_file:
        vocab |= {v.strip().lower() for v in in_file.readlines() if len(v) > 1}

    vocab |= {w.lower() for w in words.words() if len(w) > 1}

    return vocab


VOCAB = get_vocab()
