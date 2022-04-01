"""Term patterns."""
from traiter.terms.csv_ import Csv


class ExtractorTerms:
    """Terms for all extractor patterns."""

    terms = Csv.shared("time")


class AdminUnitTerms:
    """Terms used for parsing admin units."""

    terms = Csv.shared("us_locations")
    replace = terms.pattern_dict("replace")
    us_states = terms.patterns_with_label("us_state")
    us_counties = terms.patterns_with_label("us_county")
