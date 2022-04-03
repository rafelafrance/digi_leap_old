"""Parse administrative unit notations."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns
from .terms import VocabTerms


class AdminUnit:
    """Constants used to parse admin units."""

    state = ["us_state", "us_state_or_county", "us_territory"]
    county = ["us_county", "us_state_or_county"]
    any_ = ["us_state", "us_county", "us_state_or_county", "us_territory"]


# ####################################################################################
def admin_unit_decoder():
    """Get the administrative unit decoder."""
    return common_patterns.get_common_patterns() | {
        "county_label": {"LOWER": {"IN": ["co", "co.", "county"]}},
        "state_label": {"LOWER": {"IN": ["plants", "flora"]}},
        "us_state": {"ENT_TYPE": {"IN": AdminUnit.state}},
        "us_county": {"ENT_TYPE": {"IN": AdminUnit.county}},
        "of": {"LOWER": {"IN": ["of"]}},
        ":": {"POS": "PUNCT"},
    }


# ####################################################################################
ON_COUNTY_BEFORE_STATE_MATCH = "digi_leap.county_before_state.v1"


def build_county_before_state_patterns():
    """Add patterns where the county is mentioned before the state."""
    return MatcherPatterns(
        "admin_unit.county_before_state",
        on_match=ON_COUNTY_BEFORE_STATE_MATCH,
        decoder=admin_unit_decoder(),
        patterns=[
            "us_county county_label ,? us_state",
            "us_county ,? us_state",
        ],
    )


@registry.misc(ON_COUNTY_BEFORE_STATE_MATCH)
def on_county_before_state_match(ent):
    """Enrich an administrative unit match."""
    ent._.new_label = "admin_unit"
    entities = [e for e in ent.ents if e.label_ in AdminUnit.any_]
    state = entities[1].text.title()
    ent._.data["us_state"] = VocabTerms.replace.get(state, state)
    ent._.data["us_county"] = entities[0].text.title()


# ####################################################################################
ON_COUNTY_ONLY_MATCH = "digi_leap.county_only.v1"


def build_county_only_patterns():
    """Add patterns where there is a county but no state."""
    return MatcherPatterns(
        "admin_unit.county_only",
        on_match=ON_COUNTY_ONLY_MATCH,
        decoder=admin_unit_decoder(),
        patterns=[
            "us_county county_label",
        ],
    )


@registry.misc(ON_COUNTY_ONLY_MATCH)
def on_county_only_match(ent):
    """Enrich an administrative unit match."""
    ent._.new_label = "admin_unit"
    county = [e.text for e in ent.ents if e.label_ in AdminUnit.county]
    ent._.data["us_county"] = county[0].title()


# ####################################################################################
ON_STATE_BEFORE_COUNTY_MATCH = "digi_leap.state_before_county.v1"


def build_state_before_county_patterns():
    """Add patterns where the state is mentioned before the county."""
    return MatcherPatterns(
        "admin_unit.state_before_county",
        on_match=ON_STATE_BEFORE_COUNTY_MATCH,
        decoder=admin_unit_decoder(),
        patterns=[
            "us_state county_label ,? us_county",
            "state_label of? us_state county_label :? us_county",
        ],
    )


@registry.misc(ON_STATE_BEFORE_COUNTY_MATCH)
def on_state_before_county_match(ent):
    """Enrich an administrative unit match."""
    ent._.new_label = "admin_unit"
    entities = [e for e in ent.ents if e.label_ in AdminUnit.any_]
    state = entities[0].text.title()
    ent._.data["us_state"] = VocabTerms.replace.get(state, state)
    ent._.data["us_county"] = entities[1].text.title()


# ####################################################################################
ON_STATE_ONLY_MATCH = "digi_leap.state_only.v1"


def build_state_only_patterns():
    """Add patterns where there is a state but no count."""
    return MatcherPatterns(
        "admin_unit.state_only",
        on_match=ON_STATE_ONLY_MATCH,
        decoder=admin_unit_decoder(),
        patterns=[
            "state_label of? us_state",
        ],
    )


@registry.misc(ON_STATE_ONLY_MATCH)
def on_state_only_match(ent):
    """Enrich an administrative unit match."""
    ent._.new_label = "admin_unit"
    state = [e.text.title() for e in ent.ents if e.label_ in AdminUnit.state][0]
    ent._.data["us_state"] = VocabTerms.replace.get(state, state)
