from plants.pylib.const import TAXA_CSV
from plants.pylib.const import VOCAB_DIR as PLANT_VOCAB
from traiter.pylib import term_reader
from traiter.pylib.const import VOCAB_DIR as TRAITER_VOCAB

# ##########################################################################
TAXA_TERMS = term_reader.read(TAXA_CSV)
MONOMIAL_TERMS = term_reader.take(TAXA_TERMS, "monomial")
BINOMIAL_TERMS = term_reader.take(TAXA_TERMS, "binomial")

BASIC_TERMS = term_reader.shared("time")
BASIC_TERMS += term_reader.shared("labels")
BASIC_TERMS += term_reader.shared("lat_long")
BASIC_TERMS += term_reader.shared("habitat")
BASIC_TERMS += term_reader.read(PLANT_VOCAB / "ranks.csv")
BASIC_TERMS += term_reader.read(PLANT_VOCAB / "jobs.csv")
BASIC_TERMS = term_reader.drop(BASIC_TERMS, "time_units")

ALL_BASIC_TERMS = BASIC_TERMS + MONOMIAL_TERMS + BINOMIAL_TERMS
REPLACE_BASIC_TERMS = term_reader.pattern_dict(ALL_BASIC_TERMS, "replace")

# ##########################################################################
LOCATION_TERMS = term_reader.read(TRAITER_VOCAB / "us_locations.csv")

REPLACE_LOCATION_TERMS = term_reader.pattern_dict(LOCATION_TERMS, "replace")
COUNTY_IN = term_reader.pattern_dict(LOCATION_TERMS, "inside")
POSTAL = term_reader.pattern_dict(LOCATION_TERMS, "postal")
