from pathlib import Path

import regex as re
from plants.pylib.traits import terms as p_terms
from spacy.language import Language
from spacy.util import registry
from traiter.pylib import const as t_const
from traiter.pylib.pattern_compiler import ACCUMULATOR
from traiter.pylib.pattern_compiler import Compiler
from traiter.pylib.pipes import add
from traiter.pylib.pipes import reject_match
from traiter.pylib.traits import terms as t_terms

CONFLICT = ["us_county", "color"]
ALLOW = [*CONFLICT, "PERSON"]

PERSON_CSV = Path(__file__).parent / "terms" / "person_terms.csv"
NAME_CSV = Path(t_terms.__file__).parent / "name_terms.csv"
JOB_CSV = Path(p_terms.__file__).parent / "job_terms.csv"
ALL_CSVS = [PERSON_CSV, NAME_CSV, JOB_CSV]

BAD_ENT = """ month """.split()
PUNCT = "[.:;,_-]"
CONJ = ["CCONJ", "ADP"]
ID1 = r"^(\w*\d+\w*)$"
ID2 = r"^(\w*\d+\w*|[A-Za-z])$"
DASH_LIKE = r"^[._-]+$"

NAME4 = [s for s in t_const.NAME_SHAPES if len(s) > 3 and s[-1] != "."]

NICK_OPEN = t_const.OPEN + t_const.QUOTE
NICK_CLOSE = t_const.CLOSE + t_const.QUOTE

NAME_RE = "".join(t_const.OPEN + t_const.CLOSE + t_const.QUOTE + list(".,'&"))
NAME_RE = re.compile(rf"^[\sa-z{re.escape(NAME_RE)}-]+$")


def build(nlp: Language, overwrite: list[str] = None):
    add.term_pipe(nlp, name="person_terms", path=ALL_CSVS)

    overwrite = overwrite if overwrite else []
    name_overwrite = overwrite + "name_prefix name_suffix no_label".split()

    add.trait_pipe(
        nlp,
        name="name_patterns",
        compiler=name_patterns(),
        overwrite=name_overwrite,
        keep=[*ACCUMULATOR.keep, "col_label", "det_label", "no_label"],
    )

    # add.debug_tokens(nlp)  # ##########################################
    job_overwrite = (
        overwrite + """ name col_label det_label no_label other_label id_no """.split()
    )
    add.trait_pipe(
        nlp,
        name="job_patterns",
        compiler=job_patterns(),
        overwrite=job_overwrite,
    )
    # add.debug_tokens(nlp)  # ##########################################

    add.trait_pipe(
        nlp,
        name="other_collector_patterns",
        compiler=other_collector_patterns(),
        overwrite=["other_collector"],
    )
    # add.debug_tokens(nlp)  # ##########################################

    add.cleanup_pipe(nlp, name="person_cleanup")


def name_patterns():
    decoder = {
        "(": {"TEXT": {"IN": NICK_OPEN}},
        ")": {"TEXT": {"IN": NICK_CLOSE}},
        "-": {"TEXT": {"REGEX": DASH_LIKE}},
        "..": {"TEXT": {"REGEX": r"^[.]+$"}},
        ":": {"LOWER": {"REGEX": rf"^(by|{PUNCT}+)$"}},
        "A": {"TEXT": {"REGEX": r"^[A-Z][._,]?$"}},
        "_": {"TEXT": {"REGEX": r"^[._,]+$"}},
        "conflict": {"ENT_TYPE": {"IN": CONFLICT}},
        "dr": {"ENT_TYPE": "name_prefix"},
        "id1": {"LOWER": {"REGEX": ID1}},
        "id2": {"LOWER": {"REGEX": ID2}},
        "jr": {"ENT_TYPE": "name_suffix"},
        "name": {"POS": {"IN": ["PROPN", "NOUN"]}},
        "name4": {"SHAPE": {"IN": NAME4}},
        "no_label": {"ENT_TYPE": "no_label"},
        "no_space": {"SPACY": False},
        "nope": {"ENT_TYPE": "not_name"},
    }

    return [
        Compiler(
            label="name",
            on_match="person_name_match",
            decoder=decoder,
            patterns=[
                "       name name? name4",
                "       name name? name4             _? jr+",
                "       name name? name? conflict",
                "       name name? name? conflict    _? jr+",
                "       conflict   name? name? name ",
                "       conflict   name? name? name  _? jr+",
                "            A A? A?  name4",
                "            A A? A?  name4 _? jr+",
                "       name A A? A?  name4",
                "       name A A? A?  name4 _? jr+",
                "       name ..       name4",
                "       name ..       name4 _? jr+",
                "       name ( name ) name4",
                "       name ( name ) name4 _? jr+",
                "       name ( name ) name4",
                "dr+ _? name   name?  name4",
                "dr+ _? name   name?  name4             _? jr+",
                "dr+ _? name   name?  name  conflict",
                "dr+ _? name   name?  name? conflict    _? jr+",
                "dr+ _? conflict      name? name? name4",
                "dr+ _? conflict      name? name? name4 _? jr+",
                "dr+ _?      A A? A?  name4",
                "dr+ _?      A A? A?  name4 _? jr+",
                "dr+ _? name A A? A?  name4",
                "dr+ _? name A A? A?  name4 _? jr+",
                "dr+ _? name ..       name4",
                "dr+ _? name ..       name4 _? jr+",
                "dr+ _? name ( name ) name4",
                "dr+ _? name ( name ) name4 _? jr+",
                "dr+ _? name ( name ) name4",
            ],
        ),
        Compiler(
            label="not_name",
            on_match=reject_match.REJECT_MATCH,
            decoder=decoder,
            patterns=[
                "      name+ nope+",
                "nope+ name+",
                "nope+ name+ nope+",
            ],
        ),
        Compiler(
            label="id_no",
            on_match="id_no_match",
            decoder=decoder,
            patterns=[
                "             id1? no_space? id1? -? id2",
                "no_label+ :* id1? no_space? id1? -? id2",
            ],
        ),
    ]


def job_patterns():
    decoder = {
        "id1": {"LOWER": {"REGEX": ID1}},
        "id2": {"LOWER": {"REGEX": ID2}},
        "-": {"TEXT": {"REGEX": DASH_LIKE}},
        ".": {"TEXT": {"REGEX": r"^[._,]+$"}},
        ":": {"LOWER": {"REGEX": rf"^(by|{PUNCT}+)$"}},
        "and": {"POS": {"IN": CONJ}},
        "bad": {"ENT_TYPE": {"IN": BAD_ENT}},
        "by": {"LOWER": {"IN": ["by"]}},
        "col_label": {"ENT_TYPE": "col_label"},
        "det_label": {"ENT_TYPE": "det_label"},
        "id_no": {"ENT_TYPE": "id_no"},
        "maybe": {"POS": "PROPN"},
        "name": {"ENT_TYPE": "name"},
        "nope": {"ENT_TYPE": "not_name"},
        "other_label": {"ENT_TYPE": "other_label"},
        "other_col": {"ENT_TYPE": "other_collector"},
        "sep": {"LOWER": {"IN": CONJ + list("._,;")}},
    }

    return [
        Compiler(
            label="collector",
            on_match="collector_match",
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
            on_match="other_collector_match",
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
            on_match="determiner_match",
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
        "and": {"POS": {"IN": CONJ}},
        "maybe": {"POS": "PROPN"},
        "name": {"ENT_TYPE": "name"},
        "other_col": {"ENT_TYPE": "other_collector"},
        "sep": {"LOWER": {"IN": CONJ + list("._,;")}},
    }

    return [
        Compiler(
            label="other_collector2",
            id="other_collector",
            on_match="other_collector2_match",
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


@registry.misc("person_name_match")
def person_name_match(ent):
    name = ent.text
    name = re.sub(rf" ({PUNCT})", r"\1", name)
    name = re.sub(r"\.\.|_", "", name)

    if not NAME_RE.match(name.lower()):
        raise reject_match.RejectMatch

    for token in ent:
        token._.flag = "name"

        # Only accept proper nouns or nouns
        if len(token.text) > 1 and token.pos_ not in ("PROPN", "NOUN", "PUNCT"):
            raise reject_match.RejectMatch

        # If there's a digit in the name reject it
        if re.search(r"\d", token.text):
            raise reject_match.RejectMatch

        # If it is all lower case reject it
        if token.text.islower():
            raise reject_match.RejectMatch

    ent._.data = {"name": name}
    ent[0]._.data = ent._.data
    ent[0]._.flag = "name_data"


@registry.misc("collector_match")
def collector_match(ent):
    people = []
    col_no = ""

    for token in ent:

        if token._.flag == "name_data":
            people.append(token._.data["name"])

        elif token._.flag == "name" or token.ent_type_ in ("col_label", "no_label"):
            continue

        elif token._.flag == "id_no":
            col_no = token._.data["id_no"]

    if not people:
        raise reject_match.RejectMatch

    ent._.data = {"collector": people if len(people) > 1 else people[0]}
    if col_no:
        ent._.data["collector_no"] = col_no


@registry.misc("determiner_match")
def determiner_match(ent):
    people = []

    for token in ent:

        if token.ent_type_ == "det_label" or token.ent_type_ == "no_label":
            continue

        if token._.flag == "name_data":
            people.append(token._.data["name"])

        elif token._.flag == "id_no":
            ent._.data["determiner_no"] = token._.data["id_no"]

    ent._.data["determiner"] = " ".join(people)


@registry.misc("other_collector_match")
def other_collector_match(ent):
    people = []

    for token in ent:

        if token._.flag == "name_data":
            people.append(token._.data["name"])

        token._.flag = "other_col"

    ent._.data["other_collector"] = people
    ent[0]._.data = ent._.data
    ent[0]._.flag = "other_col_data"


@registry.misc("other_collector2_match")
def other_collector2_match(ent):
    people = []
    person = []

    for token in ent:

        if token._.flag == "other_col_data":
            people += token._.data["other_collector"]

        elif token._.flag == "other_col" or token.text in PUNCT:
            continue

        else:
            person.append(token.text)

    ent._.data["other_collector"] = [*people, " ".join(person)]


@registry.misc("id_no_match")
def id_no_match(ent):
    frags = [t.text for t in ent if t.ent_type_ != "no_label"]
    ent._.data["id_no"] = "".join(frags)
    ent[0]._.data = ent._.data
    ent[0]._.flag = "id_no"
