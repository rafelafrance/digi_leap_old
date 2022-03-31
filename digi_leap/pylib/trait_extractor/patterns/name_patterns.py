"""Find name notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from ..terms import common_terms

PREFIXES = " mr mr. mrs mrs. miss dr dr. ".split()
SUFFIXES = " filho ii ii. iii iii. jr jr. sr sr. ".split()

DECODER = common_terms.COMMON_PATTERNS | {
    "jr": {"LOWER": {"IN": SUFFIXES}},
    "mr": {"LOWER": {"IN": PREFIXES}},
    "person": {"ENT_TYPE": "PERSON"},
    "maybe_name": {"POS": "PROPN"},
}

NAME = MatcherPatterns(
    "name",
    on_match="digi_leap.name.v1",
    decoder=DECODER,
    patterns=[
        "mr? person+ ,? jr?",
    ],
)


@registry.misc(NAME.on_match)
def collector(_):
    """Enrich a collector match."""
    pass
