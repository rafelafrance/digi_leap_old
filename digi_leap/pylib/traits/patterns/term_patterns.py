from plants.pylib.const import TAXA_CSV
from plants.pylib.const import VOCAB_DIR as PLANT_VOCAB
from traiter.pylib import term_reader
from traiter.pylib.const import VOCAB_DIR as TRAITER_VOCAB

# ##########################################################################
TERMS1 = term_reader.shared("time")
TERMS1 += term_reader.shared("labels")
TERMS1 += term_reader.read(PLANT_VOCAB / "jobs.csv")
TERMS1 = term_reader.drop(TERMS1, "time_units")

# ##########################################################################
TERMS2 = term_reader.read(TAXA_CSV)
TERMS2 += term_reader.read(PLANT_VOCAB / "ranks.csv")
TERMS2 += term_reader.read(TRAITER_VOCAB / "us_locations.csv")

REPLACE = term_reader.pattern_dict(TERMS2, "replace")
COUNTY_IN = term_reader.pattern_dict(TERMS2, "inside")
POSTAL = term_reader.pattern_dict(TERMS2, "postal")
