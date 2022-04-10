"""Find name notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns

ON_NAME_MATCH = "digi_leap.name.v1"


def build_name_patterns():
    """Build patterns for name traits."""
    prefixes = " dr dr. mr mr. mrs mrs. miss ".split()
    suffixes = " filho ii iii jr jr. sr sr. ".split()

    return MatcherPatterns(
        "name",
        on_match=ON_NAME_MATCH,
        decoder=common_patterns.get_common_patterns()
        | {
            "jr": {"LOWER": {"IN": suffixes}},
            "dr": {"LOWER": {"IN": prefixes}},
            "person": {"ENT_TYPE": "PERSON"},
            "maybe_name": {"POS": "PROPN"},
        },
        patterns=[
            "dr? person+ ,? jr?",
        ],
    )


@registry.misc(ON_NAME_MATCH)
def on_name_match(ent):
    """Enrich a collector match."""
    if ent._.data.get("PERSON"):
        del ent._.data["PERSON"]
