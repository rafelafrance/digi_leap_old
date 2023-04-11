import re
from pathlib import Path

from plants.pylib.traits import misc
from spacy import registry
from traiter.pylib.pipes import reject_match
from traiter.pylib.traits import terms

PERSON_NAME_MATCH = "person_name_match"
COLLECTOR_MATCH = "collector_match"
DETERMINER_MATCH = "determiner_match"

CONFLICT = ["us_county", "color"]
ALLOW = CONFLICT + ["PERSON"]

PERSON_CSV = Path(__file__).parent / "person_terms.csv"
NAME_CSV = Path(terms.__file__).parent / "name_terms.csv"
JOB_CSV = Path(misc.__file__).parent / "job_label_terms.csv"
ALL_CSVS = [PERSON_CSV, NAME_CSV, JOB_CSV]

BAD_ENT = """ month """.split()
PUNCT = "[.:;,_-]"
CONJ = ["CCONJ", "ADP"]
ID_NUMBER = r"^w*\d+\w*$"
DASH_LIKE = r"^[._-]+$"


@registry.misc(PERSON_NAME_MATCH)
def person_name_match(ent):

    if any(e.label_ not in ALLOW for e in ent.ents):
        raise reject_match.RejectMatch()

    if ent._.data.get("PERSON"):
        del ent._.data["PERSON"]


@registry.misc(COLLECTOR_MATCH)
def collector_match(ent):
    people = []
    col_no = []
    name = []

    for token in ent:

        if token.ent_type_ in ("col_label", "no_label"):
            continue

        if token.ent_type_ in BAD_ENT:
            raise reject_match.RejectMatch()

        elif token.ent_type_ == "name" and not re.match(DASH_LIKE, token.text):
            name.append(token.text)

        elif match := re.match(ID_NUMBER, token.text):
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

    people = [re.sub(rf" ({PUNCT})", r"\1", p) for p in people if p]
    people = [re.sub(r"\.\.|_", "", p) for p in people if p]

    if people:
        ent._.data["collector"] = people if len(people) > 1 else people[0]


@registry.misc(DETERMINER_MATCH)
def determiner_match(ent):
    people = []
    name = []
    for token in ent:
        if token.ent_type_ == "det_label" or token.ent_type_ == "no_label":
            continue
        if match := re.search(ID_NUMBER, token.text):
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
