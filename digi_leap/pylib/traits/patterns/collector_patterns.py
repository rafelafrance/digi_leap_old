import re

from spacy.util import registry
from traiter.pylib.pattern_compilers.matcher_compiler import MatcherCompiler

from . import common_patterns

CONJ = ["CCONJ", "ADP"]
COLLECTOR_NO = r"^[A-Za-z]*\d+[A-Za-z]*$"
NUMBER_LABEL = """ number no no. num num. # """.split()
DASH_LIKE = r"^[._-]+$"
PUNCT = r"^[.:;,_-]+$"

DECODER = common_patterns.PATTERNS | {
    ":": {"TEXT": {"REGEX": PUNCT}},
    "-": {"TEXT": {"REGEX": DASH_LIKE}},
    "and": {"POS": {"IN": CONJ}},
    "by": {"LOWER": {"IN": ["by"]}},
    "col_label": {"ENT_TYPE": "col_label"},
    "col_no": {"LOWER": {"REGEX": COLLECTOR_NO}},
    "maybe": {"POS": "PROPN"},
    "num_label": {"ENT_TYPE": "no_label"},
    "name": {"ENT_TYPE": "name"},
    ".": {"TEXT": {"REGEX": r"^[._,]+$"}},
}


# ####################################################################################
COLLECTOR = MatcherCompiler(
    "collector",
    on_match="digi_leap.collector.v1",
    decoder=DECODER,
    patterns=[
        "                  name+                     num_label? :* col_no",
        "                  name+ and name+           num_label? :* col_no",
        "                  name+ and name+ and name+ num_label? :* col_no",
        "col_label  by? :* name+                     num_label? :* col_no",
        "col_label  by? :* name+ and name+           num_label? :* col_no",
        "col_label  by? :* name+",
        "col_label  by? :* name+ and name+",
        "col_label  by? :* name+ and name+ and name+ num_label? :* col_no",
        "col_label  by? :* name+ and name+ and name+",
        "col_no -? col_no? name",
        "col_no -? col_no? name  .?  name",
        "col_no -? col_no? name  .?  name+",
        "col_no -? col_no? name  .?  name  .?  name",
        "col_no -? col_no? name+ and name+",
        "col_no -? col_no? name+ and name+",
        "col_no -? col_no? name+ and name+ and name+",
        "col_label  by? :* maybe",
        "col_label  by? :* maybe .? maybe",
        "col_label  by? :* maybe .? maybe .? maybe",
        "col_label  by? :* maybe",
        "col_label  by? :* maybe                   num_label? :* col_no",
        "col_label  by? :* maybe .? maybe          num_label? :* col_no",
        "col_label  by? :* maybe .? maybe .? maybe num_label? :* col_no",
    ],
)


@registry.misc(COLLECTOR.on_match)
def on_collector_match(ent):
    people = []

    col_no = []
    name = []
    for token in ent:
        if token.ent_type_ == "col_label" or token.ent_type_ == "no_label":
            continue
        elif token.ent_type_ == "name" and not re.match(DASH_LIKE, token.text):
            name.append(token.text)
        elif match := re.match(COLLECTOR_NO, token.text):
            col_no.append(match.group(0))
        elif token.pos_ == "PROPN":
            name.append(token.text)
        elif token.pos_ in CONJ:
            people.append(" ".join(name))
            name = []
        elif (match := re.match(DASH_LIKE, token.text)) and col_no:
            col_no.append(match.group(0))

    if name:
        people.append(" ".join(name))

    if col_no:
        ent._.data["collector_no"] = "".join(col_no)

    people = [re.sub(r"\.\.|_", "", p) for p in people if p]

    if people:
        ent._.data["collector"] = people if len(people) > 1 else people[0]
