import regex as re
from spacy.util import registry
from traiter.pylib import actions
from traiter.pylib.pattern_compilers.matcher import Compiler
from traiter.pylib.patterns import common

_CONJ = ["CCONJ", "ADP"]
_COLLECTOR_NO = r"^[A-Za-z]*\d+[A-Za-z]*$"
_DASH_LIKE = r"^[._-]+$"

_NOPE = """ of gps ° elev m """.split()
_BAD_ENT = """ month """.split()
_PUNCT = "[.:;,_-]"

_DECODER = common.PATTERNS | {
    ":": {"LOWER": {"REGEX": rf"^(by|{_PUNCT}+)$"}},
    "-": {"TEXT": {"REGEX": _DASH_LIKE}},
    "and": {"POS": {"IN": _CONJ}},
    "by": {"LOWER": {"IN": ["by"]}},
    "col_label": {"ENT_TYPE": "col_label"},
    "col_no": {"LOWER": {"REGEX": _COLLECTOR_NO}},
    "maybe": {"POS": "PROPN"},
    "num_label": {"ENT_TYPE": "no_label"},
    "name": {"ENT_TYPE": "name"},
    ".": {"TEXT": {"REGEX": r"^[._,]+$"}},
    "nope": {"LOWER": {"IN": _NOPE}},
    "bad": {"ENT_TYPE": {"IN": _BAD_ENT}},
}


# ####################################################################################
COLLECTOR = Compiler(
    "collector",
    on_match="plants.collector.v1",
    decoder=_DECODER,
    patterns=[
        "             name+                     num_label? :* col_no",
        "             name+ and name+           num_label? :* col_no",
        "             name+ and name+ and name+ num_label? :* col_no",
        "col_label :* name+                     num_label? :* col_no",
        "col_label :* name+ and name+           num_label? :* col_no",
        "col_label :* name+",
        "col_label :* name+ and name+",
        "col_label :* name+ and name+ and name+ num_label? :* col_no",
        "col_label :* name+ and name+ and name+",
        "col_no       name+",
        "col_no       name+ .?  name+",
        "col_no       name+ .?  name+",
        "col_no       name+ .?  name+ .?  name+",
        "col_no       name+ and name+",
        "col_no       name+ and name+",
        "col_no       name+ and name+ and name+",
        "col_label :* maybe",
        "col_label :* maybe .? maybe",
        "col_label :* maybe .? maybe .? maybe",
        "col_label :* maybe",
        "col_label :* maybe                   num_label? :* col_no",
        "col_label :* maybe .? maybe          num_label? :* col_no",
        "col_label :* maybe .? maybe .? maybe num_label? :* col_no",
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
        if token.ent_type_ in _BAD_ENT:
            raise actions.RejectMatch()
        elif token.ent_type_ == "name" and not re.match(_DASH_LIKE, token.text):
            name.append(token.text)
        elif match := re.match(_COLLECTOR_NO, token.text):
            col_no.append(match.group(0))
        elif token.pos_ == "PROPN":
            name.append(token.text)
        elif token.pos_ in _CONJ:
            people.append(" ".join(name))
            name = []
        elif (match := re.match(_DASH_LIKE, token.text)) and col_no:
            col_no.append(match.group(0))

    if name:
        people.append(" ".join(name))

    if col_no:
        ent._.data["collector_no"] = "".join(col_no)

    people = [re.sub(rf" ({_PUNCT})", r"\1", p) for p in people if p]
    people = [re.sub(r"\.\.|_", "", p) for p in people if p]

    if people:
        ent._.data["collector"] = people if len(people) > 1 else people[0]


# ####################################################################################
NOT_COLLECTOR = Compiler(
    "not_a_collector",
    on_match=actions.REJECT_MATCH,
    decoder=_DECODER,
    patterns=[
        " maybe num_label? :* col_no nope ",
        " nope  num_label? :* col_no ",
        " maybe num_label? :* col_no bad ",
        " bad   num_label? :* col_no ",
    ],
)
