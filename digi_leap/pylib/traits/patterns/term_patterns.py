from traiter.pylib.terms.db import Db

from ... import consts


# ##########################################################################
TERM_DB = consts.DATA_DIR / "terms.sqlite"
if not TERM_DB.exists():
    TERM_DB = consts.MOCK_DIR / "terms.sqlite"

LOCAL_DB = consts.ROOT_DIR / "digi_leap" / "pylib" / "traits" / "terms.sqlite"

# ##########################################################################
EXTRACTOR_TERMS = Db()
EXTRACTOR_TERMS += Db.shared("time labels")
EXTRACTOR_TERMS += Db.select_term_set(TERM_DB, "jobs")
EXTRACTOR_TERMS += Db.select_term_set(LOCAL_DB, "not_names")

# ##########################################################################
VOCAB_TERMS = Db()
VOCAB_TERMS += Db.shared("us_locations taxon_levels")
VOCAB_TERMS += Db.select_term_set(TERM_DB, "plant_taxa")

REPLACE = VOCAB_TERMS.pattern_dict("replace")

COUNTY_IN = VOCAB_TERMS.pattern_dict("inside")
POSTAL = VOCAB_TERMS.pattern_dict("postal")

LEVEL = VOCAB_TERMS.pattern_dict("level")
LEVEL = {k: v.split() for k, v in LEVEL.items()}
