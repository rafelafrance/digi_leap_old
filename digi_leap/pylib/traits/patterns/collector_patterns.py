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
    "num_label": {"ENT_TYPE": "no_label"},
    "noise": {"TEXT": {"REGEX": r"^[._]+$"}},
    "name": {"ENT_TYPE": "name"},
    "maybe": {"POS": "PROPN"},
    "nope": {"LOWER": {"IN": ["of"]}},
    ".": {"TEXT": {"REGEX": r"^[._,]+$"}},
}


# ####################################################################################
COLLECTOR = MatcherCompiler(
    "collector",
    on_match="digi_leap.collector.v1",
    decoder=DECODER,
    patterns=[
        "                  maybe  .?  maybe             num_label? :* col_no",
        "                  maybe  .?  name+             num_label? :* col_no",
        "                  maybe  .?  maybe  .?  maybe  num_label? :* col_no",
        "                  maybe+ and maybe+            num_label? :* col_no",
        "                  maybe+ and maybe+            num_label? :* col_no",
        "                  maybe+ and maybe+ and maybe+ num_label? :* col_no",
        "col_label  by? :* maybe  .? maybe              num_label? :* col_no",
        "col_label  by? :* maybe  .? maybe",
        "col_label  by? :* maybe? name+                 num_label? :* col_no",
        "col_label  by? :* maybe+                       num_label? :* col_no",
        "col_label  by? :* name+ maybe?                 num_label? :* col_no",
        "col_label  by? :* name+",
        "col_label  by? :* maybe+",
        "col_label  by? :* maybe .? maybe",
        "col_label  by? :* maybe .? maybe .? maybe",
        "col_label  by? :* maybe+ and maybe+            num_label? :* col_no",
        "col_label  by? :* maybe+ and maybe+",
        "col_label  by? :* maybe+ and maybe+ and maybe+ num_label? :* col_no",
        "col_label  by? :* maybe+ and maybe+ and maybe+",
    ],
)


@registry.misc(COLLECTOR.on_match)
def on_collector_match(ent):
    people = []

    name = []
    for token in ent:
        if token.ent_type_ == "col_label" or token.ent_type_ == "no_label":
            continue
        if token.ent_type_ == "not_name":
            raise RejectMatch()
        if token.pos_ == "PROPN":
            name.append(token.text)
        elif token.ent_type_ == "name" and token.text not in ",:":
            name.append(token.text)
        elif token.pos_ in CONJ:
            people.append(" ".join(name))
            name = []
        elif match := re.search(COLLECTOR_NO, token.text):
            col_no = match.group(0)
            ent._.data["collector_no"] = col_no

    if name:
        people.append(" ".join(name))

    people = [p for p in people if p]

    if people:
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
