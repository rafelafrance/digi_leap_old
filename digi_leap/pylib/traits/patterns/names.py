from spacy.util import registry
from traiter.pylib import actions
from traiter.pylib.matcher_patterns import MatcherPatterns
from traiter.pylib.patterns import common

_PREFIXES = " dr dr. mr mr. mrs mrs. miss doctor ".split()
_SUFFIXES = " ii iii jr jr. sr sr. phd. phd ".split()

_NOPE = """ of gps ° elev """.split()
_CONFLICT = ["us_county", "color"]
_ALLOW = _CONFLICT + ["PERSON"]

_DECODER = common.PATTERNS | {
    "jr": {"LOWER": {"IN": _SUFFIXES}},
    "dr": {"LOWER": {"IN": _PREFIXES}},
    "person": {"ENT_TYPE": "PERSON"},
    "maybe": {"POS": "PROPN"},
    "conflict": {"ENT_TYPE": {"IN": _CONFLICT}},
    "nope": {"LOWER": {"IN": _NOPE}},
    "A": {"TEXT": {"REGEX": r"^[A-Z][._,]?$"}},
    "_": {"TEXT": {"REGEX": r"^[._,]+$"}},
    # "occupied": {"ENT_TYPE": {"IN": KEEP}},
}

NAME = MatcherPatterns(
    "name",
    on_match="digi_leap.name.v1",
    decoder=_DECODER,
    patterns=[
        "dr? person+              _? jr",
        "dr? person+  _? person   _? jr",
        "dr? person+  _? conflict _? jr",
        "dr? conflict _? person   _? jr",
        "dr? person+                   ",
        "dr? person+  _? person        ",
        "dr? person+  _? conflict      ",
        "dr? A A? maybe",
        "dr? A A? maybe _? jr",
    ],
    output=None,
)


@registry.misc(NAME.on_match)
def on_name_match(ent):
    if any(e.label_ not in _ALLOW for e in ent.ents):
        raise actions.RejectMatch()

    if ent._.data.get("PERSON"):
        del ent._.data["PERSON"]


# ####################################################################################
NOT_NAME = MatcherPatterns(
    "not_name",
    on_match=actions.REJECT_MATCH,
    decoder=_DECODER,
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
        # "occupied+",
    ],
    output=None,
)
