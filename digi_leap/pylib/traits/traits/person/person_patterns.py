from traiter.pylib.pipes.reject_match import REJECT_MATCH
from traiter.pylib.traits.pattern_compiler import Compiler

from . import person_action as act


def person_name_patterns():
    decoder = {
        "jr": {"ENT_TYPE": "name_suffix"},
        "dr": {"ENT_TYPE": "name_prefix"},
        "person": {"ENT_TYPE": "PERSON"},
        "maybe": {"POS": "PROPN"},
        "conflict": {"ENT_TYPE": {"IN": act.CONFLICT}},
        "nope": {"ENT_TYPE": "not_name"},
        "A": {"TEXT": {"REGEX": r"^[A-Z][._,]?$"}},
        "_": {"TEXT": {"REGEX": r"^[._,]+$"}},
    }

    return (
        [
            Compiler(
                label="person_name",
                on_match=act.PERSON_NAME_MATCH,
                decoder=decoder,
                patterns=[
                    "dr? person+              _? jr",
                    "dr? person+  _? person   _? jr",
                    "dr? person+  _? conflict _? jr",
                    "dr? conflict _? person   _? jr",
                    "dr? person+                   ",
                    "dr? person+  _? person        ",
                    "dr? person+  _? conflict      ",
                    "dr? A A? maybe",
                    "dr? A A? maybe _? jr",
                ],
            ),
            Compiler(
                label="not_name",
                on_match=REJECT_MATCH,
                decoder=decoder,
                patterns=[
                    "        nope+",
                    "        nope  person+",
                    "        nope  maybe+",
                    "person+ nope+",
                    "maybe+  nope+",
                    "person+ nope  person+",
                    "maybe+  nope  person+",
                    "person+ nope  maybe+",
                    "maybe+  nope  maybe+",
                ],
            ),
        ],
    )


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
        "num_label": {"ENT_TYPE": "no_label"},
    }

    return [
        Compiler(
            label="collector",
            on_match=act.COLLECTOR_MATCH,
            decoder=decoder,
            patterns=[
                "col_label+ :* name+",
                "col_label+ :* name+ and name+",
                "col_label+ :* name+ and name+ and name+ num_label* :* id_no",
                "col_label+ :* name+ and name+ and name+",
                "col_label+ :* maybe",
                "col_label+ :* maybe .? maybe",
                "col_label+ :* maybe .? maybe .? maybe",
                "col_label+ :* maybe",
                "              name+                     num_label* :* id_no? -? id_no",
                "              name+                     num_label*    id_no? -? id_no",
                "              name+ and name+           num_label* :* id_no? -? id_no",
                "              name+ and name+ and name+ num_label* :* id_no? -? id_no",
                "col_label+ :* name+                     num_label* :* id_no? -? id_no",
                "col_label+ :* name+ and name+           num_label* :* id_no? -? id_no",
                "col_label+ :* maybe                     num_label* :* id_no? -? id_no",
                "col_label+ :* maybe .? maybe            num_label* :* id_no? -? id_no",
                "col_label+ :* maybe .? maybe .? maybe   num_label* :* id_no? -? id_no",
                "id_no? -? id_no       name+",
                "id_no? -? id_no       name+ .?  name+",
                "id_no? -? id_no       name+ .?  name+",
                "id_no? -? id_no       name+ .?  name+ .?  name+",
                "id_no? -? id_no       name+ and name+",
                "id_no? -? id_no       name+ and name+",
                "id_no? -? id_no       name+ and name+ and name+",
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
