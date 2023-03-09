from plants.pylib.const import TAXA_CSV
from plants.pylib.const import VOCAB_DIR as PLANT_VOCAB
from traiter.pylib import term_reader
from traiter.pylib.const import VOCAB_DIR as TRAITER_VOCAB

# ##########################################################################
TAXA_TERMS = term_reader.read(TAXA_CSV)
MONOMIAL_TERMS = term_reader.take(TAXA_TERMS, "monomial")
BINOMIAL_TERMS = term_reader.take(TAXA_TERMS, "binomial")


TERMS1 = term_reader.shared("time")
TERMS1 += term_reader.shared("labels")
TERMS1 += term_reader.shared("lat_long")
TERMS1 += term_reader.shared("habitat")
TERMS1 += term_reader.read(PLANT_VOCAB / "ranks.csv")
TERMS1 += term_reader.read(PLANT_VOCAB / "jobs.csv")
TERMS1 = term_reader.drop(TERMS1, "time_units")

ALL_TERMS1 = TERMS1 + MONOMIAL_TERMS + BINOMIAL_TERMS
REPLACE1 = term_reader.pattern_dict(ALL_TERMS1, "replace")

# ##########################################################################
TERMS2 = term_reader.read(TRAITER_VOCAB / "us_locations.csv")

REPLACE2 = term_reader.pattern_dict(TERMS2, "replace")
COUNTY_IN = term_reader.pattern_dict(TERMS2, "inside")
POSTAL = term_reader.pattern_dict(TERMS2, "postal")
