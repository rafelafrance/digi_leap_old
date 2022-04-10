"""Term patterns."""
import json
import os
from pathlib import Path

from traiter.terms.db import Db


# ##########################################################################
class Locations:
    curr_dir = Path(os.getcwd())
    is_subdir = curr_dir.name in ("notebooks", "experiments")
    root_dir = Path(".." if is_subdir else ".")
    vocab_dir = root_dir / "digi_leap" / "pylib" / "trait_extractor" / "vocabulary"
    data_dir = root_dir / "data"
    term_db = vocab_dir / "terms.sqlite"


# ##########################################################################
class Terms:
    ruler = None
    terms = None

    @classmethod
    def add_ruler(cls, nlp):
        cls.ruler = nlp.add_pipe(
            "entity_ruler",
            name="term_ruler",
            before="parser",
            config={"phrase_matcher_attr": "LOWER"},
        )


# ##########################################################################
class ExtractorTerms(Terms):
    """Terms for all the basic traits."""

    ruler_file_name = "extractor_term_ruler.jsonl"

    @classmethod
    def load_terms(cls, nlp, path):
        cls.add_ruler(nlp)
        cls.ruler.from_disk(path / cls.ruler_file_name)

    @classmethod
    def save_terms(cls, path):
        cls.ruler.to_disk(path / cls.ruler_file_name)

    @classmethod
    def build_terms(cls, nlp):
        """Build the terms from the raw CSV files."""
        cls.add_ruler(nlp)

        cls.terms = Db.shared("time")
        cls.terms += Db.select_term_set(Locations.term_db, "jobs")

        cls.ruler.add_patterns(cls.terms.for_entity_ruler())


# ##########################################################################
class VocabTerms(Terms):
    """Terms used for parsing traits with a large vocabulary."""

    replace_file_name = "replace_vocab_terms.json"
    ruler_file_name = "vocab_term_ruler.jsonl"
    level_file_name = "taxon_levels.json"

    level = None
    replace = None

    @classmethod
    def load_terms(cls, nlp, path):
        cls.add_ruler(nlp)
        cls.ruler.from_disk(path / cls.ruler_file_name)

        with open(path / cls.level_file_name) as in_file:
            cls.level = json.load(in_file)

        with open(path / cls.replace_file_name) as in_file:
            cls.replace = json.load(in_file)

    @classmethod
    def save_terms(cls, path):
        cls.ruler.to_disk(path / cls.ruler_file_name)

        with open(path / cls.level_file_name, "w") as out_file:
            json.dump(cls.level, out_file)

        with open(path / cls.replace_file_name, "w") as out_file:
            json.dump(cls.replace, out_file)

    @classmethod
    def build_terms(cls, nlp):
        """Build the terms from the raw CSV files."""
        cls.add_ruler(nlp)

        cls.terms = Db()
        cls.terms.no_clobber = True
        cls.terms.silent = True

        cls.terms += Db.shared("us_locations taxon_levels")
        cls.terms += Db.select_term_set(Locations.term_db, "plant_taxa")

        cls.replace = cls.terms.pattern_dict("replace")

        cls.level = cls.terms.pattern_dict("level")
        cls.level = {k: v.split() for k, v in cls.level.items()}

        cls.ruler.add_patterns(cls.terms.for_entity_ruler())
