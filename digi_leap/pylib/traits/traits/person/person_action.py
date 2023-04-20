import re
from pathlib import Path

from plants.pylib.traits import misc
from spacy.util import registry
from traiter.pylib import const as t_const
from traiter.pylib.pipes.reject_match import RejectMatch
from traiter.pylib.traits import terms

PERSON_NAME_MATCH = "person_name_match"
COLLECTOR_MATCH = "collector_match"
OTHER_COLLECTOR_MATCH = "other_collector_match"
DETERMINER_MATCH = "determiner_match"

CONFLICT = ["us_county", "color"]
ALLOW = [*CONFLICT, "PERSON"]

PERSON_CSV = Path(__file__).parent / "person_terms.csv"
NAME_CSV = Path(terms.__file__).parent / "name_terms.csv"
JOB_CSV = Path(misc.__file__).parent / "job_terms.csv"
ALL_CSVS = [PERSON_CSV, NAME_CSV, JOB_CSV]

BAD_ENT = """ month """.split()
PUNCT = "[.:;,_-]"
CONJ = ["CCONJ", "ADP"]
ID1 = r"^(\w*\d+\w*)$"
ID2 = r"^(\w*\d+\w*|[A-Za-z])$"
DASH_LIKE = r"^[._-]+$"

NICK_OPEN = t_const.OPEN + t_const.QUOTE
NICK_CLOSE = t_const.CLOSE + t_const.QUOTE

NAME_RE = "".join(t_const.OPEN + t_const.CLOSE + t_const.QUOTE + list(".,'&"))
NAME_RE = re.compile(rf"^[\sa-z{re.escape(NAME_RE)}-]+$")

TITLE_SHAPES = """ Xxxxx Xxxx Xxx Xx X. Xx. X """.split()
UPPER_SHAPES = """ XXXXX XXXX XXX XX X. XX. X """.split()
NAME_SHAPES = TITLE_SHAPES + UPPER_SHAPES

TITLE_SHAPES3 = """ Xxxxx Xxxx Xxx """.split()
UPPER_SHAPES3 = """ XXXXX XXXX XXX """.split()
NAME_SHAPES3 = TITLE_SHAPES3 + UPPER_SHAPES3


@registry.misc(PERSON_NAME_MATCH)
def person_name_match(ent):

    name = ent.text
    name = re.sub(rf" ({PUNCT})", r"\1", name)
    name = re.sub(r"\.\.|_", "", name)

    if len(name.split()[-1]) < 3 or not NAME_RE.match(name.lower()):
        raise RejectMatch

    for token in ent:
        token._.flag = "name"

    ent._.data["name"] = name
    ent[0]._.data = ent._.data
    ent[0]._.flag = "name_data"


@registry.misc(COLLECTOR_MATCH)
def collector_match(ent):
    people = []
    col_no = []

    for token in ent:

        if token._.flag == "name_data":
            people.append(token._.data["name"])

        elif token._.flag == "name":
            continue

        if token.ent_type_ in ("col_label", "no_label"):
            continue

        if match := re.match(ID2, token.text):
            col_no.append(match.group(0))

    if not people:
        raise RejectMatch

    if col_no:
        ent._.data["collector_no"] = "-".join(col_no)

    ent._.data["collector"] = people if len(people) > 1 else people[0]


@registry.misc(OTHER_COLLECTOR_MATCH)
def other_collector_match(ent):
    people = []

    for token in ent:

        if token._.flag == "name_data":
            people.append(token._.data["name"])

    ent._.data["other_collector"] = people


@registry.misc(DETERMINER_MATCH)
def determiner_match(ent):
    people = []
    name = []

    for token in ent:
        if token.ent_type_ == "det_label" or token.ent_type_ == "no_label":
            continue

        if match := re.search(ID1, token.text):
            if name:
                people.append(" ".join(name))
                name = []
            det_no = match.group(0)
            ent._.data["determiner_no"] = det_no

        elif token.pos_ == "PROPN" or token.ent_type_ == "name":
            name.append(token.text)

    if name:
        people.append(" ".join(name))

    ent._.data["determiner"] = " ".join(people)
