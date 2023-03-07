from spacy.util import registry
from traiter.pylib.actions import RejectMatch
from traiter.pylib.pattern_compilers.matcher_compiler import MatcherCompiler

from . import common_patterns
from . import term_patterns


STATE_ENTS = ["us_state", "us_state-us_county", "us_territory"]
COUNTY_ENTS = ["us_county", "us_state-us_county"]
ADMIN_ENTS = ["us_state", "us_county", "us_state-us_county", "us_territory"]
CO_LABEL = ["co", "co.", "county", "parish", "par", "par.", "ph.", "ph"]
ST_LABEL = ["plants", "flora"]

# ####################################################################################
DECODER = common_patterns.PATTERNS | {
    "co_label": {"LOWER": {"IN": CO_LABEL}},
    "co_word": {"LOWER": {"IN": ["county"]}},
    "st_label": {"LOWER": {"IN": ST_LABEL}},
    "us_state": {"ENT_TYPE": {"IN": STATE_ENTS}},
    "us_county": {"ENT_TYPE": {"IN": COUNTY_ENTS}},
    "of": {"LOWER": {"IN": ["of"]}},
    ",": {"TEXT": {"REGEX": r"^[:._;,]+$"}},
}


# ####################################################################################
COUNTY_STATE = MatcherCompiler(
    "admin_unit.county_state",
    on_match="digi_leap.county_state.v1",
    decoder=DECODER,
    patterns=[
        "us_county co_label ,? us_state",
    ],
)


@registry.misc(COUNTY_STATE.on_match)
def on_county_state_match(ent):
    ent._.new_label = "admin_unit"
    ent._.data["us_state"] = format_state(ent, ent_index=1)
    ent._.data["us_county"] = format_county(ent, ent_index=0)


# ####################################################################################
COUNTY_STATE_IFFY = MatcherCompiler(
    "admin_unit.county_state_iffy",
    on_match="digi_leap.county_state_iffy.v1",
    decoder=DECODER,
    patterns=[
        "us_county ,? us_state",
    ],
)


@registry.misc(COUNTY_STATE_IFFY.on_match)
def on_county_state_iffy_match(ent):
    sub_ents = [e for e in ent.ents if e.label_ in ADMIN_ENTS]

    county_ent = sub_ents[0]
    state_ent = sub_ents[1]

    if is_county_not_colorado(state_ent, county_ent):
        ent._.data["us_county"] = format_county(ent, ent_index=0)
        keep_only(ent, COUNTY_ENTS, CO_LABEL)
    elif not county_in_state(state_ent, county_ent):
        raise RejectMatch()
    else:
        ent._.data["us_state"] = format_state(ent, ent_index=1)
        ent._.data["us_county"] = format_county(ent, ent_index=0)

    ent._.new_label = "admin_unit"


def is_county_not_colorado(state_ent, county_ent):
    """Flag if Co = county label or CO = Colorado."""
    return state_ent.text == "CO" and county_ent.text.isupper()


# ####################################################################################
COUNTY_ONLY = MatcherCompiler(
    "admin_unit.county_only",
    on_match="digi_leap.county_only.v1",
    decoder=DECODER,
    patterns=[
        "us_county co_label",
        "co_word :? us_county",
    ],
)


@registry.misc(COUNTY_ONLY.on_match)
def on_county_only_match(ent):
    ent._.new_label = "admin_unit"
    ent._.data["us_county"] = format_county(ent, ent_index=0)


# ####################################################################################
STATE_COUNTY = MatcherCompiler(
    "admin_unit.state_county",
    on_match="digi_leap.state_county.v1",
    decoder=DECODER,
    patterns=[
        "us_state co_label? ,? us_county",
        "st_label of? us_state co_label ,? us_county",
    ],
)


@registry.misc(STATE_COUNTY.on_match)
def on_state_county_match(ent):
    ent._.new_label = "admin_unit"
    ent._.data["us_state"] = format_state(ent, ent_index=0)
    ent._.data["us_county"] = format_county(ent, ent_index=1)


# ####################################################################################
STATE_ONLY = MatcherCompiler(
    "admin_unit.state_only",
    on_match="digi_leap.state_only.v1",
    decoder=DECODER,
    patterns=[
        "st_label of? ,? us_state",
    ],
)


@registry.misc(STATE_ONLY.on_match)
def on_state_only_match(ent):
    ent._.new_label = "admin_unit"
    ent._.data["us_state"] = format_state(ent, ent_index=0)


# ####################################################################################
def format_state(ent, *, ent_index: int):
    sub_ents = [e for e in ent.ents if e.label_ in ADMIN_ENTS]
    state = sub_ents[ent_index].text
    st_key = get_state_key(state)
    return term_patterns.REPLACE.get(st_key, state)


def get_state_key(state):
    return state.upper() if len(state) <= 2 else state.lower()


def format_county(ent, *, ent_index: int):
    sub_ents = [e.text for e in ent.ents if e.label_ in ADMIN_ENTS]
    return sub_ents[ent_index].title()


def county_in_state(state_ent, county_ent):
    st_key = get_state_key(state_ent.text)
    co_key = county_ent.text.lower()
    return term_patterns.POSTAL[st_key] in term_patterns.COUNTY_IN[co_key]


def keep_only(ent, ent_list, label_list):
    """Trim the entity to only the state or the county."""
    start, end = 999_999_999, -1
    for token in ent:
        if token.ent_type_ in ent_list or token.text.lower() in label_list:
            start = min(start, token.i)
            end = max(end, token.i + 1)
    ent.start = start
    ent.end = end
