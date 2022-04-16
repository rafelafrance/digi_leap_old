"""Find name notations on herbarium specimen labels."""
from spacy.util import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns

PREFIXES = " dr dr. mr mr. mrs mrs. miss doctor ".split()
SUFFIXES = " filho ii iii jr jr. sr sr. phd. phd ".split()

NAME = MatcherPatterns(
    "name",
    on_match="digi_leap.name.v1",
    decoder=common_patterns.PATTERNS
    | {
        "jr": {"LOWER": {"IN": SUFFIXES}},
        "dr": {"LOWER": {"IN": PREFIXES}},
        "person": {"ENT_TYPE": "PERSON"},
        "maybe_name": {"POS": "PROPN"},
    },
    patterns=[
        "dr? person+ ,? jr?",
    ],
)


@registry.misc(NAME.on_match)
def on_name_match(ent):
    if ent._.data.get("PERSON"):
        del ent._.data["PERSON"]
