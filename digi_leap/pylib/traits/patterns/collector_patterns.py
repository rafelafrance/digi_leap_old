import re

from spacy.util import registry
from traiter.pylib.actions import REJECT_MATCH
from traiter.pylib.actions import RejectMatch
from traiter.pylib.pattern_compilers.matcher_compiler import MatcherCompiler

from . import common_patterns

CONJ = ["CCONJ", "ADP"]
COLLECTOR_NO = r"^\w*\d+\w*$"
NUMBER_LABEL = """ number no no. num num. # """.split()

DECODER = common_patterns.PATTERNS | {
    ":": {"TEXT": {"REGEX": r"^[:._;]+$"}},
    "and": {"POS": {"IN": CONJ}},
    "by": {"LOWER": {"IN": ["by"]}},
    "col_label": {"ENT_TYPE": "col_label"},
    "col_no": {"LOWER": {"REGEX": COLLECTOR_NO}},
    "no_label": {"ENT_TYPE": "no_label"},
    "noise": {"TEXT": {"REGEX": r"^[._]+$"}},
    "name": {"ENT_TYPE": "name"},
    "maybe": {"POS": "PROPN"},
    "nope": {"LOWER": {"IN": ["of"]}},
}


# ####################################################################################
COLLECTOR = MatcherCompiler(
    "collector",
    on_match="digi_leap.collector.v1",
    decoder=DECODER,
    patterns=[
        "                  name+                        no_label? :* col_no",
        "                  name+  and   name+           no_label? :* col_no",
        "                  name+  and   name+ and name+ no_label? :* col_no",
        "                  name+  noise name+           no_label? :* col_no",
        "col_label  by? :* maybe  maybe                 no_label? :* col_no",
        "col_label  by? :* maybe  maybe",
        "col_label  by? :* maybe+ and   name+           no_label? :* col_no",
        "col_label  by? :* maybe+ name+                 no_label? :* col_no",
        "col_label  by? :* name+                        no_label? :* col_no",
        "col_label  by? :* name+  and   name+           no_label? :* col_no",
        "col_label  by? :* name+  and   name+ and name+ no_label? :* col_no",
        "col_label  by? :* name+  and   name+ and name+ no_label? :* col_no?",
        "col_label  by? :* name+  and   name+",
        "col_label  by? :* name+  maybe?",
        "col_label  by? :* name+  maybe+                no_label? :* col_no",
        "col_label  by? :* name+  noise name+           no_label? :* col_no",
        "col_label  by? :* name+  noise name+",
    ],
)


@registry.misc(COLLECTOR.on_match)
def on_collector_match(ent):
    people = []

    # Get the names and numbers
    name = []
    for token in ent:
        if token.ent_type_ == "col_label" or token.ent_type_ == "no_label":
            continue
        if token.pos_ == "PROPN" or token.ent_type_ == "name":
            name.append(token.text)
        else:
            if name:
                people.append(" ".join(name))
                name = []
            if match := re.search(COLLECTOR_NO, token.text):
                col_no = match.group(0)
                ent._.data["collector_no"] = col_no
    if name:
        people.append(" ".join(name))

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


# ####################################################################################
NOT_COLLECTOR = MatcherCompiler(
    "not_collector",
    on_match=REJECT_MATCH,
    decoder=DECODER,
    patterns=[
        " nope name+ ",
    ],
)
