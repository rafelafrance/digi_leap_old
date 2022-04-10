"""Find determiner notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

DETERMINER = MatcherPatterns(
    "determiner",
    on_match="digi_leap.determiner.v1",
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


@registry.misc(DETERMINER.on_match)
def on_determiner_match(ent):
    name = [t.text for t in ent if t.ent_type_ == "name"]
    ent._.data["determiner"] = name[0]
