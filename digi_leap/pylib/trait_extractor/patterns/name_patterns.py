"""Find collector notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

MIN_LEN = 5  # Minimum collector name length


NAME = MatcherPatterns(
    "name",
    on_match="digi_leap.name.v1",
    decoder={
        "name_part": {"ENT_TYPE": "name_part"},
        "A.": {"TEXT": {"REGEX": r"^[A-Z]\.$"}},
        "Aaa": {"TEXT": {"REGEX": r"^[A-Z][[:alpha:]*$"}},
    },
    patterns=[
        "name_part+",
        "name_part Aaa* name_part+",
        "A.+ Aaa* name_part+",
    ],
)


@registry.misc(NAME.on_match)
def name(ent):
    """Enrich a name pattern."""
    print(ent)
