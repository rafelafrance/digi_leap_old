import re

from spacy.util import registry
from traiter.pylib.pattern_compilers.matcher import Compiler

_DETERMINER_NO = r"^\w*\d+\w*$"

DETERMINER = Compiler(
    "determiner",
    on_match="plants.determiner.v1",
    decoder={
        ":": {"TEXT": {"REGEX": r"^[:._,;]+$"}},
        "by": {"LOWER": {"IN": ["by"]}},
        "det_label": {"ENT_TYPE": "det_label"},
        "name": {"ENT_TYPE": "name"},
        "maybe": {"POS": "PROPN"},
        "det_no": {"LOWER": {"REGEX": _DETERMINER_NO}},
        "num_label": {"ENT_TYPE": "no_label"},
    },
    patterns=[
        "det_label by? :* maybe? name+",
        "det_label by? :* name+ num_label? :* det_no",
    ],
)


@registry.misc(DETERMINER.on_match)
def on_determiner_match(ent):
    people = []
    name = []
    for token in ent:
        if token.ent_type_ == "det_label" or token.ent_type_ == "no_label":
            continue
        if match := re.search(_DETERMINER_NO, token.text):
            if name:
                people.append(" ".join(name))
                name = []
            det_no = match.group(0)
            ent._.data["determiner_no"] = det_no
        elif token.pos_ == "PROPN" or token.ent_type_ == "name":
            name.append(token.text)
    if name:
        people.append(" ".join(name))
    ent._.data["determiner"] = " ".join(people)
