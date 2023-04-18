from pathlib import Path

from spacy import registry
from traiter.pipes import reject_match
from traiter.traits import terms
from traiter.traits import trait_util

COUNTY_STATE_MATCH = "county_state_match"
COUNTY_STATE_IFFY_MATCH = "county_state_iffy_match"
COUNTY_ONLY_MATCH = "county_only_match"
STATE_COUNTY_MATCH = "state_county_match"
STATE_ONLY_MATCH = "state_only_match"

ADMIN_UNIT_CSV = Path(__file__).parent / "admin_unit_terms.csv"
US_LOCATIONS_CSV = Path(terms.__file__).parent / "us_location_terms.csv"
ALL_CSVS = [US_LOCATIONS_CSV, ADMIN_UNIT_CSV]


REPLACE = trait_util.term_data(ALL_CSVS, "replace")
COUNTY_IN = trait_util.term_data(ALL_CSVS, "inside")
POSTAL = trait_util.term_data(ALL_CSVS, "postal")

STATE_ENTS = ["us_state", "us_state-us_county", "us_territory"]
COUNTY_ENTS = ["us_county", "us_state-us_county"]
ADMIN_ENTS = ["us_state", "us_county", "us_state-us_county", "us_territory"]


@registry.misc(COUNTY_STATE_MATCH)
def county_state_match(ent):
    if len(ent.ents) < 2:
        raise reject_match.RejectMatch

    ent._.data["us_state"] = format_state(ent, ent_index=1)
    ent._.data["us_county"] = format_county(ent, ent_index=0)


@registry.misc(COUNTY_STATE_IFFY_MATCH)
def county_state_iffy_match(ent):
    sub_ents = [e for e in ent.ents if e.label_ in [*ADMIN_ENTS, "county_label_iffy"]]

    if len(sub_ents) < 2:
        raise reject_match.RejectMatch

    county_ent = sub_ents[0]
    state_ent = sub_ents[1]

    if is_county_not_colorado(state_ent, county_ent):
        ent._.data["us_county"] = format_county(ent, ent_index=0)

    elif not county_in_state(state_ent, county_ent):
        raise reject_match.RejectMatch

    else:
        ent._.data["us_state"] = format_state(ent, ent_index=1)
        ent._.data["us_county"] = format_county(ent, ent_index=0)


@registry.misc(COUNTY_ONLY_MATCH)
def county_only_match(ent):
    ent._.data["us_county"] = format_county(ent, ent_index=0)


@registry.misc(STATE_COUNTY_MATCH)
def state_county_match(ent):
    ent._.data["us_state"] = format_state(ent, ent_index=0)
    ent._.data["us_county"] = format_county(ent, ent_index=1)


@registry.misc(STATE_ONLY_MATCH)
def state_only_match(ent):
    ent._.data["us_state"] = format_state(ent, ent_index=0)


def format_state(ent, *, ent_index: int):
    sub_ents = [e for e in ent.ents if e.label_ in ADMIN_ENTS]
    state = sub_ents[ent_index].text
    st_key = get_state_key(state)
    return REPLACE.get(st_key, state)


def format_county(ent, *, ent_index: int):
    sub_ents = [e.text for e in ent.ents if e.label_ in ADMIN_ENTS]
    return sub_ents[ent_index].title()


def is_county_not_colorado(state_ent, county_ent):
    """Flag if Co = county label or CO = Colorado."""
    return state_ent.text == "CO" and county_ent.text.isupper()


def get_state_key(state):
    return state.upper() if len(state) <= 2 else state.lower()


def county_in_state(state_ent, county_ent):
    st_key = get_state_key(state_ent.text)
    co_key = county_ent.text.lower()
    return POSTAL.get(st_key, "") in COUNTY_IN[co_key]
