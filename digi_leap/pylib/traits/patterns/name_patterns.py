from spacy.util import registry
from traiter.pylib.pattern_compilers.matcher_compiler import MatcherCompiler

from . import common_patterns

PREFIXES = " dr dr. mr mr. mrs mrs. miss doctor ".split()
SUFFIXES = " ii iii jr jr. sr sr. phd. phd ".split()

NAME = MatcherCompiler(
    "name",
    on_match="digi_leap.name.v1",
    decoder=common_patterns.PATTERNS
    | {
        "jr": {"LOWER": {"IN": SUFFIXES}},
        "dr": {"LOWER": {"IN": PREFIXES}},
        "person": {"ENT_TYPE": "PERSON"},
        "maybe": {"POS": "PROPN"},
        "A": {"TEXT": {"REGEX": r"^[A-Z]\.?$"}},
    },
    patterns=[
        "dr? person+ ,? jr?",
        "dr? A A? maybe",
        "dr? A A? maybe ,? jr",
    ],
)


@registry.misc(NAME.on_match)
def on_name_match(ent):
    if ent._.data.get("PERSON"):
        del ent._.data["PERSON"]
