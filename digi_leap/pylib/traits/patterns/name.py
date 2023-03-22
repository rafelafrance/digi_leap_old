from spacy.util import registry
from traiter.pylib import actions
from traiter.pylib.pattern_compilers.matcher import Compiler
from traiter.pylib.patterns.common import PATTERNS

from .terms import KEEP

PREFIXES = " dr dr. mr mr. mrs mrs. miss doctor ".split()
SUFFIXES = " ii iii jr jr. sr sr. phd. phd ".split()

NOPE = """ of gps ° elev """.split()

DECODER = PATTERNS | {
    "jr": {"LOWER": {"IN": SUFFIXES}},
    "dr": {"LOWER": {"IN": PREFIXES}},
    "person": {"ENT_TYPE": "PERSON"},
    "maybe": {"POS": "PROPN"},
    "conflict": {"ENT_TYPE": "us_county"},
    "nope": {"LOWER": {"IN": NOPE}},
    "A": {"TEXT": {"REGEX": r"^[A-Z][._,]?$"}},
    "_": {"TEXT": {"REGEX": r"^[._,]+$"}},
    "occupied": {"ENT_TYPE": {"IN": KEEP}},
}

NAME = Compiler(
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
    if any(e.label_ != "PERSON" for e in ent.ents):
        raise actions.RejectMatch()

    if ent._.data.get("PERSON"):
        del ent._.data["PERSON"]


# ####################################################################################
NOT_NAME = Compiler(
    "not_name",
    on_match=actions.REJECT_MATCH,
    decoder=DECODER,
    patterns=[
        "        nope+ ",
        "        nope  person+ ",
        "        nope  maybe+ ",
        "person+ nope+ ",
        "maybe+  nope+ ",
        "person+ nope  person+",
        "maybe+  nope  person+",
        "person+ nope  maybe+",
        "maybe+  nope  maybe+",
        "occupied+",
    ],
)
