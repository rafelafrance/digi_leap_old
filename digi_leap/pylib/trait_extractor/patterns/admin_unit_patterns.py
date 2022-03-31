"""Parse administrative unit notations."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from ..terms import admin_unit_terms
from ..terms import common_terms

A_STATE = ["us_state", "us_state_or_county", "us_territory"]
A_COUNTY = ["us_county", "us_state_or_county"]
ADMIN_UNIT = ["us_state", "us_county", "us_state_or_county", "us_territory"]

DECODER = common_terms.COMMON_PATTERNS | {
    "county_label": {"LOWER": {"IN": ["co", "co.", "county"]}},
    "state_label": {"LOWER": {"IN": ["plants", "flora"]}},
    "us_state": {"ENT_TYPE": {"IN": A_STATE}},
    "us_county": {"ENT_TYPE": {"IN": A_COUNTY}},
    "of": {"LOWER": {"IN": ["of"]}},
    ":": {"POS": "PUNCT"},
}

COUNTY_BEFORE_STATE = MatcherPatterns(
    "admin_unit.county_before_state",
    on_match="digi_leap.county_before_state.v1",
    decoder=DECODER,
    patterns=[
        "us_county county_label ,? us_state",
        "us_county ,? us_state",
    ],
)


COUNTY_ONLY = MatcherPatterns(
    "admin_unit.county_only",
    on_match="digi_leap.county_only.v1",
    decoder=DECODER,
    patterns=[
        "us_county county_label",
    ],
)

STATE_BEFORE_COUNTY = MatcherPatterns(
    "admin_unit.state_before_county",
    on_match="digi_leap.state_before_county.v1",
    decoder=DECODER,
    patterns=[
        "us_state county_label ,? us_county",
        "state_label of? us_state county_label :? us_county",
    ],
)


STATE_ONLY = MatcherPatterns(
    "admin_unit.state_only",
    on_match="digi_leap.state_only.v1",
    decoder=DECODER,
    patterns=[
        "state_label of? us_state",
    ],
)


@registry.misc(STATE_ONLY.on_match)
def state_only(ent):
    """Enrich an administrative unit match."""
    ent._.new_label = "admin_unit"
    state = [e.text.title() for e in ent.ents if e.label_ in A_STATE][0]
    ent._.data["us_state"] = admin_unit_terms.REPLACE.get(state, state)


@registry.misc(COUNTY_ONLY.on_match)
def county_only(ent):
    """Enrich an administrative unit match."""
    ent._.new_label = "admin_unit"
    county = [e.text for e in ent.ents if e.label_ in A_COUNTY]
    ent._.data["us_county"] = county[0].title()


@registry.misc(STATE_BEFORE_COUNTY.on_match)
def state_before_county(ent):
    """Enrich an administrative unit match."""
    ent._.new_label = "admin_unit"
    entities = [e for e in ent.ents if e.label_ in ADMIN_UNIT]
    state = entities[0].text.title()
    ent._.data["us_state"] = admin_unit_terms.REPLACE.get(state, state)
    ent._.data["us_county"] = entities[1].text.title()


@registry.misc(COUNTY_BEFORE_STATE.on_match)
def county_before_state(ent):
    """Enrich an administrative unit match."""
    ent._.new_label = "admin_unit"
    entities = [e for e in ent.ents if e.label_ in ADMIN_UNIT]
    state = entities[1].text.title()
    ent._.data["us_state"] = admin_unit_terms.REPLACE.get(state, state)
    ent._.data["us_county"] = entities[0].text.title()
