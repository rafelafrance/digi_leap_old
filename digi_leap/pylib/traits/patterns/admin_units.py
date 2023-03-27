from spacy.util import registry
from traiter.pylib import actions
from traiter.pylib.matcher_patterns import MatcherPatterns
from traiter.pylib.patterns import common

from ... import const

_COUNTY_IN = const.ADMIN_UNIT_TERMS.pattern_dict("inside")
_POSTAL = const.ADMIN_UNIT_TERMS.pattern_dict("postal")

_STATE_ENTS = ["us_state", "us_state-us_county", "us_territory"]
_COUNTY_ENTS = ["us_county", "us_state-us_county"]
_ADMIN_ENTS = ["us_state", "us_county", "us_state-us_county", "us_territory"]
_ST_LABEL = ["plants", "flora"]
_CO_LABEL = ["co", "co.", "county", "parish", "par", "par.", "ph.", "ph"]

_BAD_PREFIX = """ of """.split()
_BAD_SUFFIX = """ road mountain lake university """.split()


# ####################################################################################
_DECODER = common.PATTERNS | {
    "co_label": {"LOWER": {"IN": _CO_LABEL}},
    "co_word": {"LOWER": {"IN": ["county"]}},
    "st_label": {"LOWER": {"IN": _ST_LABEL}},
    "us_state": {"ENT_TYPE": {"IN": _STATE_ENTS}},
    "us_county": {"ENT_TYPE": {"IN": _COUNTY_ENTS}},
    "of": {"LOWER": {"IN": ["of"]}},
    ",": {"TEXT": {"REGEX": r"^[:._;,]+$"}},
    "bad_prefix": {"LOWER": {"IN": _BAD_PREFIX}},
    "bad_suffix": {"LOWER": {"IN": _BAD_SUFFIX}},
}


# ####################################################################################
COUNTY_STATE = MatcherPatterns(
    "admin_unit.county_state",
    on_match="digi_leap.county_state.v1",
    decoder=_DECODER,
    patterns=[
        "us_county co_label ,? us_state",
    ],
    output=["admin_unit"],
)


@registry.misc(COUNTY_STATE.on_match)
def on_county_state_match(ent):
    ent._.new_label = "admin_unit"
    ent._.data["us_state"] = format_state(ent, ent_index=1)
    ent._.data["us_county"] = format_county(ent, ent_index=0)


# ####################################################################################
COUNTY_STATE_IFFY = MatcherPatterns(
    "admin_unit.county_state_iffy",
    on_match="digi_leap.county_state_iffy.v1",
    decoder=_DECODER,
    patterns=[
        "us_county ,? us_state",
    ],
    output=["admin_unit"],
)


@registry.misc(COUNTY_STATE_IFFY.on_match)
def on_county_state_iffy_match(ent):
    sub_ents = [e for e in ent.ents if e.label_ in _ADMIN_ENTS]

    county_ent = sub_ents[0]
    state_ent = sub_ents[1]

    if is_county_not_colorado(state_ent, county_ent):
        ent._.data["us_county"] = format_county(ent, ent_index=0)
        keep_only(ent, _COUNTY_ENTS, _CO_LABEL)
    elif not county_in_state(state_ent, county_ent):
        raise actions.RejectMatch()
    else:
        ent._.data["us_state"] = format_state(ent, ent_index=1)
        ent._.data["us_county"] = format_county(ent, ent_index=0)

    ent._.new_label = "admin_unit"


def is_county_not_colorado(state_ent, county_ent):
    """Flag if Co = county label or CO = Colorado."""
    return state_ent.text == "CO" and county_ent.text.isupper()


# ####################################################################################
COUNTY_ONLY = MatcherPatterns(
    "admin_unit.county_only",
    on_match="digi_leap.county_only.v1",
    decoder=_DECODER,
    patterns=[
        "us_county co_label",
        "co_word :? us_county",
    ],
    output=["admin_unit"],
)


@registry.misc(COUNTY_ONLY.on_match)
def on_county_only_match(ent):
    ent._.new_label = "admin_unit"
    ent._.data["us_county"] = format_county(ent, ent_index=0)


# ####################################################################################
STATE_COUNTY = MatcherPatterns(
    "admin_unit.state_county",
    on_match="digi_leap.state_county.v1",
    decoder=_DECODER,
    patterns=[
        "us_state co_label? ,? us_county co_label?",
        "st_label of? us_state co_label ,? us_county co_label?",
    ],
    output=["admin_unit"],
)


@registry.misc(STATE_COUNTY.on_match)
def on_state_county_match(ent):
    ent._.new_label = "admin_unit"
    ent._.data["us_state"] = format_state(ent, ent_index=0)
    ent._.data["us_county"] = format_county(ent, ent_index=1)


# ####################################################################################
STATE_ONLY = MatcherPatterns(
    "admin_unit.state_only",
    on_match="digi_leap.state_only.v1",
    decoder=_DECODER,
    patterns=[
        "st_label of? ,? us_state",
    ],
    output=["admin_unit"],
)


@registry.misc(STATE_ONLY.on_match)
def on_state_only_match(ent):
    ent._.new_label = "admin_unit"
    ent._.data["us_state"] = format_state(ent, ent_index=0)


# ####################################################################################
NOT_COUNTY = MatcherPatterns(
    "not_county",
    on_match=actions.REJECT_MATCH,
    decoder=_DECODER,
    patterns=[
        "bad_prefix us_county",
        "           us_county bad_suffix",
        "bad_prefix us_county bad_suffix",
    ],
    output=["admin_unit"],
)


# ####################################################################################
def format_state(ent, *, ent_index: int):
    sub_ents = [e for e in ent.ents if e.label_ in _ADMIN_ENTS]
    state = sub_ents[ent_index].text
    st_key = get_state_key(state)
    return const.ADMIN_UNIT_TERMS.replace.get(st_key, state)


def get_state_key(state):
    return state.upper() if len(state) <= 2 else state.lower()


def format_county(ent, *, ent_index: int):
    sub_ents = [e.text for e in ent.ents if e.label_ in _ADMIN_ENTS]
    return sub_ents[ent_index].title()


def county_in_state(state_ent, county_ent):
    st_key = get_state_key(state_ent.text)
    co_key = county_ent.text.lower()
    return _POSTAL[st_key] in _COUNTY_IN[co_key]


def keep_only(ent, ent_list, label_list):
    """Trim the entity to only the state or the county."""
    start, end = 999_999_999, -1
    for token in ent:
        if token.ent_type_ in ent_list or token.text.lower() in label_list:
            start = min(start, token.i)
            end = max(end, token.i + 1)
    ent.start = start
    ent.end = end
