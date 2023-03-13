from spacy.util import registry
from traiter.pylib.actions import REJECT_MATCH
from traiter.pylib.pattern_compilers.matcher_compiler import MatcherCompiler

from . import common_patterns

PREFIXES = " dr dr. mr mr. mrs mrs. miss doctor ".split()
SUFFIXES = " ii iii jr jr. sr sr. phd. phd ".split()

NOPE = """ of gps ° elev """.split()

DECODER = common_patterns.PATTERNS | {
    "jr": {"LOWER": {"IN": SUFFIXES}},
    "dr": {"LOWER": {"IN": PREFIXES}},
    "person": {"ENT_TYPE": "PERSON"},
    "maybe": {"POS": "PROPN"},
    "conflict": {"ENT_TYPE": "us_county"},
    "nope": {"LOWER": {"IN": NOPE}},
    "A": {"TEXT": {"REGEX": r"^[A-Z][._,]?$"}},
    "_": {"TEXT": {"REGEX": r"^[._,]+$"}},
}

NAME = MatcherCompiler(
    "name",
    on_match="digi_leap.name.v1",
    decoder=DECODER,
    patterns=[
        "dr? person+              _? jr",
        "dr? person+  _? person   _? jr",
        "dr? person+  _? conflict _? jr",
        "dr? conflict _? person   _? jr",
        "dr? person+                   ",
        "dr? person+  _? person        ",
        "dr? A A? maybe",
        "dr? A A? maybe _? jr",
    ],
)


@registry.misc(NAME.on_match)
def on_name_match(ent):
    if ent._.data.get("PERSON"):
        del ent._.data["PERSON"]


# ####################################################################################
NOT_name = MatcherCompiler(
    "not_name",
    on_match=REJECT_MATCH,
    decoder=DECODER,
    patterns=[
        "         nope+ ",
        "         nope  person+ ",
        "         nope  maybe+ ",
        " person+ nope+ ",
        " maybe+  nope+ ",
        " person+ nope  person+",
        " maybe+  nope  person+",
        " person+ nope  maybe+",
        " maybe+  nope  maybe+",
    ],
)
