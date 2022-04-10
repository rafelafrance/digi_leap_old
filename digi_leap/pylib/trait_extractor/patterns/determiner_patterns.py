"""Find determiner notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

ON_DETERMINER_MATCH = "digi_leap.determiner.v1"


def build_determiner_patterns():
    """Build patterns for determiner traits."""
    return MatcherPatterns(
        "determiner",
        on_match=ON_DETERMINER_MATCH,
        decoder={
            ":": {"TEXT": {"REGEX": r"^[:._,]+$"}},
            "by": {"LOWER": {"IN": ["by"]}},
            "det_label": {"ENT_TYPE": "det_label"},
            "name": {"ENT_TYPE": "name"},
        },
        patterns=[
            "det_label by? :? name+",
        ],
    )


@registry.misc(ON_DETERMINER_MATCH)
def on_determiner_match(ent):
    """Enrich a determiner match."""
    name = [t.text for t in ent if t.ent_type_ == "name"]
    ent._.data["determiner"] = name[0]
