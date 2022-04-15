"""Parse administrative unit notations."""
from spacy.util import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns
from . import term_utils


STATE_ENTS = ["us_state", "us_state-us_county", "us_territory"]
COUNTY_ENTS = ["us_county", "us_state-us_county"]
ADMIN_ENTS = ["us_state", "us_county", "us_state-us_county", "us_territory"]


# ####################################################################################
def admin_unit_decoder():
    return common_patterns.PATTERNS | {
        "county_label": {"LOWER": {"IN": ["co", "co.", "county"]}},
        "state_label": {"LOWER": {"IN": ["plants", "flora"]}},
        "us_state": {"ENT_TYPE": {"IN": STATE_ENTS}},
        "us_county": {"ENT_TYPE": {"IN": COUNTY_ENTS}},
        "of": {"LOWER": {"IN": ["of"]}},
        ":": {"POS": "PUNCT"},
    }


# ####################################################################################
COUNTY_BEFORE_STATE = MatcherPatterns(
    "admin_unit.county_before_state",
    on_match="digi_leap.county_before_state.v1",
    decoder=admin_unit_decoder(),
    patterns=[
        "us_county county_label ,? us_state",
        "us_county ,? us_state",
    ],
)


@registry.misc(COUNTY_BEFORE_STATE.on_match)
def on_county_before_state_match(ent):
    ent._.new_label = "admin_unit"
    entities = [e for e in ent.ents if e.label_ in ADMIN_ENTS]
    state = entities[1].text.title()
    ent._.data["us_state"] = term_utils.REPLACE.get(state, state)
    ent._.data["us_county"] = entities[0].text.title()


# ####################################################################################
COUNTY_ONLY = MatcherPatterns(
    "admin_unit.county_only",
    on_match="digi_leap.county_only.v1",
    decoder=admin_unit_decoder(),
    patterns=[
        "us_county county_label",
    ],
)


@registry.misc(COUNTY_ONLY.on_match)
def on_county_only_match(ent):
    ent._.new_label = "admin_unit"
    county = [e.text for e in ent.ents if e.label_ in COUNTY_ENTS]
    ent._.data["us_county"] = county[0].title()


# ####################################################################################
STATE_BEFORE_COUNTY = MatcherPatterns(
    "admin_unit.state_before_county",
    on_match="digi_leap.state_before_county.v1",
    decoder=admin_unit_decoder(),
    patterns=[
        "us_state county_label ,? us_county",
        "state_label of? us_state county_label :? us_county",
    ],
)


@registry.misc(STATE_BEFORE_COUNTY.on_match)
def on_state_before_county_match(ent):
    ent._.new_label = "admin_unit"
    entities = [e for e in ent.ents if e.label_ in ADMIN_ENTS]
    state = entities[0].text.title()
    ent._.data["us_state"] = term_utils.REPLACE.get(state, state)
    ent._.data["us_county"] = entities[1].text.title()


# ####################################################################################
STATE_ONLY = MatcherPatterns(
    "admin_unit.state_only",
    on_match="digi_leap.state_only.v1",
    decoder=admin_unit_decoder(),
    patterns=[
        "state_label of? :? us_state",
    ],
)


@registry.misc(STATE_ONLY.on_match)
def on_state_only_match(ent):
    ent._.new_label = "admin_unit"
    state = [e.text.title() for e in ent.ents if e.label_ in STATE_ENTS][0]
    ent._.data["us_state"] = term_utils.REPLACE.get(state, state)
