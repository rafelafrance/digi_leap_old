"""Find collector notations on herbarium specimen labels."""
import re

from spacy.util import registry
from traiter.actions import RejectMatch
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns

CONJ = ["CCONJ", "ADP"]
COLLECTOR_NO = r"^\w*\d+\w*$"
NUMBER_LABEL = """ number no no. num num. # """.split()


COLLECTOR = MatcherPatterns(
    "collector",
    on_match="digi_leap.collector.v1",
    decoder=common_patterns.PATTERNS
    | {
        ":": {"TEXT": {"REGEX": r"^[:._]+$"}},
        "and": {"POS": {"IN": CONJ}},
        "by": {"LOWER": {"IN": ["by"]}},
        "col_label": {"ENT_TYPE": "col_label"},
        "col_no": {"LOWER": {"REGEX": COLLECTOR_NO}},
        "no_label": {"LOWER": {"IN": NUMBER_LABEL}},
        "noise": {"TEXT": {"REGEX": r"^[._]+$"}},
        "name": {"ENT_TYPE": "name"},
        "maybe": {"POS": "PROPN"},
    },
    patterns=[
        "col_label? by? :? name+ no_label? :? col_no",
        "col_label  by? :? name+ no_label? :? col_no?",
        "col_label? by? :? name+ and name+ no_label? :? col_no",
        "col_label  by? :? name+ and name+ no_label? :? col_no?",
        "col_label? by? :? name+ noise name+ no_label? col_no",
        "col_label  by? :? name+ noise name+ no_label? col_no?",
        "col_label? by? :? name+ and name+ and name+ no_label? :? col_no",
        "col_label  by? :? name+ and name+ and name+ no_label? :? col_no?",
        #
        "col_label  by? :? maybe+ and name+ no_label? col_no?",
    ],
)


@registry.misc(COLLECTOR.on_match)
def on_collector_match(ent):
    people = []

    # Get the names and numbers
    for token in ent:
        if token.ent_type_ == "col_label" or token.lower_ in NUMBER_LABEL:
            continue
        if token.pos_ == "PROPN" or token.ent_type_ == "name":
            people.append(token.text)
        elif match := re.search(COLLECTOR_NO, token.text):
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

    # All that for nothing
    if not people:
        raise RejectMatch()

    # Format output
    ent._.data["collector"] = people if len(people) > 1 else people[0]
