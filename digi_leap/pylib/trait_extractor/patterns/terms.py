"""Term patterns."""
import os
from pathlib import Path

from traiter.terms.csv_ import Csv


# ##########################################################################
# Vocabulary locations
class Dir:
    """File locations."""

    curr_dir = Path(os.getcwd())
    is_subdir = curr_dir.name in ("notebooks", "experiments")
    root_dir = Path(".." if is_subdir else ".")
    vocab_dir = root_dir / "digi_leap" / "pylib" / "trait_extractor" / "vocabulary"


# ##########################################################################
class ExtractorTerms:
    """Terms for all the basic traits."""

    terms = Csv.shared("time")


# ##########################################################################
class VocabTerms:
    """Terms used for parsing traits with a large vocabulary."""

    terms = Csv.shared("us_locations")
    terms += Csv.read_csv(Dir.vocab_dir / "itis_plant_taxa.csv")

    replace = terms.pattern_dict("replace")

    level = terms.pattern_dict("level")
    level = {k: v.split() for k, v in level.items()}

    us_states = terms.patterns_with_label("us_state")
    us_counties = terms.patterns_with_label("us_county")
