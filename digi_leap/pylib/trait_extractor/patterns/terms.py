"""Term patterns."""
import os
from pathlib import Path

from traiter.terms.db import Db


# ##########################################################################
CURR_DIR = Path(os.getcwd())
IS_SUBDIR = CURR_DIR.name in ("notebooks", "experiments")
ROOT_DIR = Path(".." if IS_SUBDIR else ".")
VOCAB_DIR = ROOT_DIR / "digi_leap" / "pylib" / "trait_extractor" / "vocabulary"
DATA_DIR = ROOT_DIR / "data"
TERM_DB = VOCAB_DIR / "terms.sqlite"


# ##########################################################################
EXTRACTOR_TERMS = Db.shared("time")
EXTRACTOR_TERMS += Db.select_term_set(TERM_DB, "jobs")


# ##########################################################################
VOCAB_TERMS = Db()
VOCAB_TERMS.no_clobber = True
VOCAB_TERMS.silent = True

VOCAB_TERMS += Db.shared("us_locations taxon_levels")
VOCAB_TERMS += Db.select_term_set(TERM_DB, "plant_taxa")

VOCAB_REPLACE = VOCAB_TERMS.pattern_dict("replace")

LEVEL = VOCAB_TERMS.pattern_dict("level")
LEVEL = {k: v.split() for k, v in LEVEL.items()}
