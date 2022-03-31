"""Literals used in the system."""
from traiter.terms.csv_ import Csv

# #########################################################################
TERMS = Csv.shared("time")

REPLACE = TERMS.pattern_dict("replace")
