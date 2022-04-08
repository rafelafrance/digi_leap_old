"""Term patterns."""
import os
from pathlib import Path

from traiter.terms.db import Db


# ##########################################################################
# Vocabulary locations
class Locations:
    """File locations."""

    curr_dir = Path(os.getcwd())
    is_subdir = curr_dir.name in ("notebooks", "experiments")
    root_dir = Path(".." if is_subdir else ".")
    vocab_dir = root_dir / "digi_leap" / "pylib" / "trait_extractor" / "vocabulary"
    data_dir = root_dir / "data"
    term_db = vocab_dir / "terms.sqlite"


# ##########################################################################
class ExtractorTerms:
    """Terms for all the basic traits."""

    terms = Db.shared("time")


# ##########################################################################
class VocabTerms:
    """Terms used for parsing traits with a large vocabulary."""

    terms = Db()
    terms.no_clobber = True
    terms.silent = True

    terms += Db.shared("us_locations taxon_levels")
    terms += Db.select_term_set(Locations.term_db, "plant_taxa")

    replace = terms.pattern_dict("replace")

    level = terms.pattern_dict("level")
    level = {k: v.split() for k, v in level.items()}

    us_states = terms.patterns_with_label("us_state")
    us_counties = terms.patterns_with_label("us_county")
