from traiter.pylib.pipes.reject_match import REJECT_MATCH
from traiter.pylib.traits.pattern_compiler import Compiler

from . import person_action as act


def name_patterns():
    decoder = {
        "(": {"TEXT": {"IN": act.NICK_OPEN}},
        ")": {"TEXT": {"IN": act.NICK_CLOSE}},
        "-": {"TEXT": {"REGEX": act.DASH_LIKE}},
        "..": {"TEXT": {"REGEX": r"^[.]+$"}},
        ":": {"LOWER": {"REGEX": rf"^(by|{act.PUNCT}+)$"}},
        "A": {"TEXT": {"REGEX": r"^[A-Z][._,]?$"}},
        "_": {"TEXT": {"REGEX": r"^[._,]+$"}},
        "conflict": {"ENT_TYPE": {"IN": act.CONFLICT}},
        "dr": {"ENT_TYPE": "name_prefix"},
        "id1": {"LOWER": {"REGEX": act.ID1}},
        "id2": {"LOWER": {"REGEX": act.ID2}},
        "jr": {"ENT_TYPE": "name_suffix"},
        "name": {"POS": "PROPN"},
        "name3": {"SHAPE": {"IN": act.NAME_SHAPES3}},
        "no_label": {"ENT_TYPE": "no_label"},
        "no_space": {"SPACY": False},
        "nope": {"ENT_TYPE": "not_name"},
    }

    return [
        Compiler(
            label="name",
            on_match=act.PERSON_NAME_MATCH,
            decoder=decoder,
            patterns=[
                "      name name? name3",
                "      name name? name3             _? jr",
                "      name name? name3 conflict",
                "      name name? name? conflict    _? jr",
                "      conflict   name? name? name3",
                "      conflict   name? name? name3 _? jr",
                "           A A? A?  name3",
                "           A A? A?  name3   _? jr",
                "      name A A? A?  name3",
                "      name A A? A?  name3 _? jr",
                "      name ..       name3",
                "      name ..       name3 _? jr",
                "      name ( name ) name3",
                "      name ( name ) name3 _? jr",
                "      name ( name ) name3",
                "dr _? name name? name3",
                "dr _? name name? name3             _? jr",
                "dr _? name name? name3 conflict",
                "dr _? name name? name? conflict    _? jr",
                "dr _? conflict   name? name? name3",
                "dr _? conflict   name? name? name3 _? jr",
                "dr _?      A A? A?  name3",
                "dr _?      A A? A?  name3 _? jr",
                "dr _? name A A? A?  name3",
                "dr _? name A A? A?  name3 _? jr",
                "dr _? name ..       name3",
                "dr _? name ..       name3 _? jr",
                "dr _? name ( name ) name3",
                "dr _? name ( name ) name3 _? jr",
                "dr _? name ( name ) name3",
            ],
        ),
        Compiler(
            label="not_name",
            on_match=REJECT_MATCH,
            decoder=decoder,
            patterns=[
                "      name+ nope+",
                "nope+ name+",
                "nope+ name+ nope+",
            ],
        ),
        Compiler(
            label="id_no",
            on_match=act.ID_NO_MATCH,
            decoder=decoder,
            patterns=[
                "             id1? no_space? id1? -? id2",
                "no_label+ :* id1? no_space? id1? -? id2",
            ],
        ),
    ]


def job_patterns():
    decoder = {
        "id1": {"LOWER": {"REGEX": act.ID1}},
        "id2": {"LOWER": {"REGEX": act.ID2}},
        "-": {"TEXT": {"REGEX": act.DASH_LIKE}},
        ".": {"TEXT": {"REGEX": r"^[._,]+$"}},
        ":": {"LOWER": {"REGEX": rf"^(by|{act.PUNCT}+)$"}},
        "and": {"POS": {"IN": act.CONJ}},
        "bad": {"ENT_TYPE": {"IN": act.BAD_ENT}},
        "by": {"LOWER": {"IN": ["by"]}},
        "col_label": {"ENT_TYPE": "col_label"},
        "det_label": {"ENT_TYPE": "det_label"},
        "id_no": {"ENT_TYPE": "id_no"},
        "maybe": {"POS": "PROPN"},
        "name": {"ENT_TYPE": "name"},
        "nope": {"ENT_TYPE": "not_name"},
        "other_label": {"ENT_TYPE": "other_label"},
        "other_col": {"ENT_TYPE": "other_collector"},
        "sep": {"LOWER": {"IN": act.CONJ + list("._,;")}},
    }

    return [
        Compiler(
            label="collector",
            on_match=act.COLLECTOR_MATCH,
            keep="collector",
            decoder=decoder,
            patterns=[
                "col_label+ :* name+",
                "col_label+ :* name+ and name+",
                "col_label+ :* name+ and name+ and name+",
                "col_label+ :* name+                     id_no+",
                "col_label+ :* name+ and name+           id_no+",
                "col_label+ :* name+ and name+ and name+ id_no+",
                "              name+                     id_no+",
                "              name+ and name+           id_no+",
                "              name+ and name+ and name+ id_no+",
                "id_no+        name+",
                "id_no+        name+ and name+",
                "id_no+        name+ and name+ and name+",
            ],
        ),
        Compiler(
            label="other_collector",
            on_match=act.OTHER_COLLECTOR_MATCH,
            keep="other_collector",
            decoder=decoder,
            patterns=[
                "other_label+ name+ ",
                "other_label+ name+ sep* name+ ",
                "other_label+ name+ sep* name+ sep* name+ ",
                "other_label+ name+ sep* name+ sep* name+ sep* name+ ",
                (
                    "other_label+ name+ sep* name+ sep* name+ sep* name+ sep* name+ "
                    "sep* name+"
                ),
            ],
        ),
        Compiler(
            label="determiner",
            on_match=act.DETERMINER_MATCH,
            keep="determiner",
            decoder=decoder,
            patterns=[
                "det_label+ by? :* maybe? name+",
                "det_label+ by? :* name+ id_no+",
            ],
        ),
    ]


def other_collector_patterns():
    decoder = {
        "and": {"POS": {"IN": act.CONJ}},
        "maybe": {"POS": "PROPN"},
        "name": {"ENT_TYPE": "name"},
        "other_col": {"ENT_TYPE": "other_collector"},
        "sep": {"LOWER": {"IN": act.CONJ + list("._,;")}},
    }

    return [
        Compiler(
            label="other_collector2",
            id="other_collector",
            on_match=act.OTHER_COLLECTOR2_MATCH,
            keep="other_collector",
            decoder=decoder,
            patterns=[
                " other_col+ sep* name+ ",
                " other_col+ sep* maybe ",
                " other_col+ sep* name  and name+ ",
                " other_col+ sep* maybe and maybe maybe ",
            ],
        ),
    ]
