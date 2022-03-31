"""Find collector notations on herbarium specimen labels."""
import re

from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from ..terms import common_terms

CONJ = ["CCONJ", "ADP"]
COL_NO = r"^\w*\d+\w*$"
COLL_LABEL = """ collector collected coll coll. col col. """.split()
NUM_LABEL = """ number no no. num num. # """.split()


DECODER = common_terms.COMMON_PATTERNS | {
    ":": {"TEXT": {"REGEX": r"^[:._]+$"}},
    "and": {"POS": {"IN": CONJ}},
    "by": {"LOWER": {"IN": ["by"]}},
    "col_label": {"LOWER": {"IN": COLL_LABEL}},
    "col_no": {"LOWER": {"REGEX": COL_NO}},
    "no_label": {"LOWER": {"IN": NUM_LABEL}},
    "noise": {"TEXT": {"REGEX": r"^[._]+$"}},
    "name": {"ENT_TYPE": "name"},
    "maybe": {"POS": "PROPN"},
}

COLLECTOR = MatcherPatterns(
    "collector",
    on_match="digi_leap.collector.v1",
    decoder=DECODER,
    patterns=[
        "col_label? by? :? name+ no_label? :? col_no",
        "col_label  by? :? name+ no_label? :? col_no?",
        "col_label? by? :? name+ and name+ no_label? :? col_no",
        "col_label  by? :? name+ and name+ no_label? :? col_no?",
        "col_label? by? :? name+ noise name+ no_label? col_no",
        "col_label  by? :? name+ noise name+ no_label? col_no?",
        "col_label? by? :? name+ and name+ and name+ no_label? :? col_no",
        "col_label  by? :? name+ and name+ and name+ no_label? :? col_no?",
        "col_label  by? :? maybe+ and name+ no_label? col_no?",
    ],
)


@registry.misc(COLLECTOR.on_match)
def collector(ent):
    """Enrich a collector match."""
    people = []

    # Get the names and numbers
    for token in ent:
        if token.lower_ in NUM_LABEL or token.lower_ in COLL_LABEL:
            pass
        elif token.pos_ == "PROPN":
            people.append(token.text)
        elif token.pos_ in CONJ:
            pass
        elif match := re.search(COL_NO, token.text):
            col_no = match.group(0)
            ent._.data["collector_no"] = col_no

    # Fix names with noise in them. "_Wayne.. Hutchins" which will parse as
    # two names ["Wayne", "Hutchins"] should be one name "Wayne Hutchins".
    new = people[:1]
    for i in range(1, len(people)):
        prev = people[i - 1]
        curr = people[i]
        if len(prev.split()) == 1 and len(curr.split()) == 1:
            new.pop()
            new.append(f"{prev} {curr}")
        else:
            new.append(curr)

    # Clean up names
    people = [re.sub(r",", "", p) for p in new]
    people = [re.sub(r"\s\s+", " ", p) for p in people]

    # Format output
    ent._.data["collector"] = people if len(new) > 1 else people[0]
