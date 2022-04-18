"""Find determiner notations on herbarium specimen labels."""
import re

from spacy.util import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

DETERMINER_NO = r"^\w*\d+\w*$"
NUMBER_LABEL = """ number no no. num num. # """.split()

DETERMINER = MatcherPatterns(
    "determiner",
    on_match="digi_leap.determiner.v1",
    decoder={
        ":": {"TEXT": {"REGEX": r"^[:._,;]+$"}},
        "by": {"LOWER": {"IN": ["by"]}},
        "det_label": {"ENT_TYPE": "det_label"},
        "name": {"ENT_TYPE": "name"},
        "maybe": {"POS": "PROPN"},
        "det_no": {"LOWER": {"REGEX": DETERMINER_NO}},
        "no_label": {"LOWER": {"IN": NUMBER_LABEL}},
    },
    patterns=[
        "det_label by? :* name+",
        "det_label by? :* name+ no_label? :* det_no",
    ],
)


@registry.misc(DETERMINER.on_match)
def on_determiner_match(ent):
    names = []
    for token in ent:
        if token.ent_type_ == "det_label" or token.lower_ in NUMBER_LABEL:
            continue
        if match := re.search(DETERMINER_NO, token.text):
            det_no = match.group(0)
            ent._.data["determiner_no"] = det_no
        elif token.pos_ == "PROPN" or token.ent_type_ == "name":
            names.append(token.text)

        ent._.data["determiner"] = " ".join(names)
