from traiter.pylib.pipes.reject_match import REJECT_MATCH
from traiter.pylib.traits.pattern_compiler import Compiler

from . import person_action as act


def name_patterns():
    decoder = {
        "A": {"TEXT": {"REGEX": r"^[A-Z][._,]?$"}},
        "_": {"TEXT": {"REGEX": r"^[._,]+$"}},
        "..": {"TEXT": {"REGEX": r"^[.]+$"}},
        "conflict": {"ENT_TYPE": {"IN": act.CONFLICT}},
        "dr": {"ENT_TYPE": "name_prefix"},
        "jr": {"ENT_TYPE": "name_suffix"},
        "name": {"POS": "PROPN"},
        "nope": {"ENT_TYPE": "not_name"},
        # "name": {"SHAPE": {"IN": act.NAME_SHAPES}},
        "name3": {"SHAPE": {"IN": act.NAME_SHAPES3}},
    }

    return [
        Compiler(
            label="name",
            on_match=act.PERSON_NAME_MATCH,
            decoder=decoder,
            patterns=[
                "dr? name name? name3",
                "dr? name name? name3             _? jr",
                "dr? name name? name3 conflict",
                "dr? name name? name? conflict    _? jr",
                "dr? conflict   name? name? name3",
                "dr? conflict   name? name? name3 _? jr",
                "dr? A A? name",
                "dr? A A? name      _? jr",
                "dr? name A A name3",
                "dr? name A A name3 _? jr",
                "dr? name ..  name3",
                "dr? name ..  name3 _? jr",
            ],
        ),
        Compiler(
            label="not_name",
            on_match=REJECT_MATCH,
            decoder=decoder,
            patterns=[
                "      nope+",
                "      nope+ name+",
                "name+ nope+",
                "name+ nope+ name+",
            ],
        ),
    ]


def job_patterns():
    decoder = {
        "-": {"TEXT": {"REGEX": act.DASH_LIKE}},
        ".": {"TEXT": {"REGEX": r"^[._,]+$"}},
        ":": {"LOWER": {"REGEX": rf"^(by|{act.PUNCT}+)$"}},
        "and": {"POS": {"IN": act.CONJ}},
        "bad": {"ENT_TYPE": {"IN": act.BAD_ENT}},
        "by": {"LOWER": {"IN": ["by"]}},
        "col_label": {"ENT_TYPE": "col_label"},
        "det_label": {"ENT_TYPE": "det_label"},
        "id_no": {"LOWER": {"REGEX": act.ID_NUMBER}},
        "maybe": {"POS": "PROPN"},
        "name": {"ENT_TYPE": "name"},
        "nope": {"ENT_TYPE": "not_name"},
        "other_label": {"ENT_TYPE": "other_label"},
        "num_label": {"ENT_TYPE": "no_label"},
        "sep": {"LOWER": {"IN": act.CONJ + list("._,;")}},
    }

    return [
        Compiler(
            label="collector",
            on_match=act.COLLECTOR_MATCH,
            decoder=decoder,
            patterns=[
                "col_label+ :* name+",
                "col_label+ :* name+ and name+",
                "col_label+ :* name+ and name+ and name+ num_label* :* id_no? -? id_no",
                "col_label+ :* name+ and name+ and name+",
                "col_label+ :* maybe",
                "col_label+ :* maybe .? maybe",
                "col_label+ :* maybe .? maybe .? maybe",
                "col_label+ :* maybe",
                "              name+                     num_label* :* id_no? -? id_no",
                "              name+ and name+           num_label* :* id_no? -? id_no",
                "              name+ and name+ and name+ num_label* :* id_no? -? id_no",
                "col_label+ :* name+                     num_label* :* id_no? -? id_no",
                "col_label+ :* name+ and name+           num_label* :* id_no? -? id_no",
                "col_label+ :* maybe                     num_label* :* id_no? -? id_no",
                "col_label+ :* maybe .? maybe            num_label* :* id_no? -? id_no",
                "col_label+ :* maybe .? maybe .? maybe   num_label* :* id_no? -? id_no",
                "id_no? -? id_no        name+",
                "id_no? -? id_no        name+ .?  name+",
                "id_no? -? id_no        name+ .?  name+",
                "id_no? -? id_no        name+ .?  name+ .?  name+",
                "id_no? -? id_no        name+ and name+",
                "id_no? -? id_no        name+ and name+",
                "id_no? -? id_no        name+ and name+ and name+",
            ],
        ),
        Compiler(
            label="other_collector",
            on_match=act.OTHER_COLLECTOR_MATCH,
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
            label="not_collector",
            on_match=REJECT_MATCH,
            decoder=decoder,
            patterns=[
                " maybe num_label* :* id_no nope ",
                " nope  num_label* :* id_no ",
                " maybe num_label* :* id_no bad ",
                " bad   num_label* :* id_no ",
            ],
        ),
        Compiler(
            label="determiner",
            on_match=act.DETERMINER_MATCH,
            decoder=decoder,
            patterns=[
                "det_label+ by? :* maybe? name+",
                "det_label+ by? :* name+ num_label* :* id_no",
            ],
        ),
    ]
