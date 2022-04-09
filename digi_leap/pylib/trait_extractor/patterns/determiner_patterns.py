"""Find determiner notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns

ON_DETERMINER_MATCH = "digi_leap.determiner.v1"


def build_determiner_patterns():
    """Build patterns for collector traits."""
    return MatcherPatterns(
        "determiner",
        on_match=ON_DETERMINER_MATCH,
        decoder=common_patterns.get_common_patterns()
        | {
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
    name = []
    for token in ent:
        if token._.cached_label == "det_label":
            continue
        elif token.pos_ == "PROPN":
            name.append(token.text)
    ent._.data["determiner"] = " ".join(name)
    if ent._.data.get("PERSON"):
        del ent._.data["PERSON"]
