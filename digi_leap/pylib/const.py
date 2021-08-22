"""Define literals used in the system."""

import os
from pathlib import Path

import nltk
import numpy as np
import torch

# Common defaults
DEVICE: str = "cuda:0" if torch.cuda.is_available() else "cpu"
GPU_BATCH: int = 2
NMS_THRESHOLD: float = 0.3
PROC_BATCH = 10
ROW_BATCH = 1_000_000  # How many records to work with at a time
SBS_THRESHOLD: float = 0.95
WORKERS: int = 2

# Directories and files
CURR_DIR = Path(os.getcwd())
IS_SUBDIR = CURR_DIR.name in ("notebooks", "experiments")

ROOT_DIR = Path(".." if IS_SUBDIR else ".")

VOCAB_DIR = ROOT_DIR / "vocab"
FONTS_DIR = ROOT_DIR / "fonts"
DATA_DIR = ROOT_DIR / "data"

PROCESSED_DIR = DATA_DIR / "processed"

CSV_FILE = "occurrence_raw.csv"
DB = PROCESSED_DIR / "occurrence_raw_2021-02.sqlite3.db"

# OCR defaults
CHAR_BLACKLIST = "¥€£¢$«»®©§{}[]<>|"
TESS_LANG = "eng"
TESS_CONFIG = " ".join(
    [
        f"-l {TESS_LANG}",
        f"-c tessedit_char_blacklist='{CHAR_BLACKLIST}'",
    ]
)

# Graphics defaults
HORIZ_ANGLES = np.array([0.0, 0.5, -0.5, 1.0, -1.0, 1.5, -1.5, 2.0, -2.0])
NEAR_HORIZ = np.deg2rad(HORIZ_ANGLES)
NEAR_VERT = np.deg2rad(np.linspace(88.0, 92.0, num=9))
NEAR_HORIZ, NEAR_VERT = NEAR_VERT, NEAR_HORIZ  # ?!


# Vocabulary for scoring OCR quality
def get_vocab() -> set[str]:
    """Get the vocabulary used for scoring OCR quality."""
    vocab = set()
    with open(VOCAB_DIR / "plant_taxa.txt") as in_file:
        vocab |= {v.strip().lower() for v in in_file.readlines() if len(v) > 1}
    vocab |= {w.lower() for w in nltk.corpus.words.words() if len(w) > 1}
    return vocab


VOCAB = get_vocab()
