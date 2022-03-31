"""Literals used in the system."""
from traiter.terms.csv_ import Csv


# #########################################################################
TERMS = Csv.shared("us_locations")

REPLACE = TERMS.pattern_dict("replace")

US_STATES = TERMS.patterns_with_label("us_state")
US_COUNTIES = TERMS.patterns_with_label("us_county")
