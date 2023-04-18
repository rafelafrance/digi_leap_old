from traiter.pipes import reject_match
from traiter.pylib import const as t_const
from traiter.traits.pattern_compiler import Compiler

from . import admin_unit_action as act


def admin_unit_patterns():
    decoder = {
        ",": {"TEXT": {"REGEX": r"^[:._;,]+$"}},
        ":": {"TEXT": {"IN": t_const.COLON}},
        "co_label": {"ENT_TYPE": "county_label"},
        "co_word": {"LOWER": {"IN": ["county"]}},
        "of": {"LOWER": {"IN": ["of"]}},
        "st_label": {"ENT_TYPE": "state_label"},
        "us_county": {"ENT_TYPE": {"IN": act.COUNTY_ENTS}},
        "us_state": {"ENT_TYPE": {"IN": act.STATE_ENTS}},
    }
    return [
        Compiler(
            label="county_state",
            id="admin_unit",
            on_match=act.COUNTY_STATE_MATCH,
            decoder=decoder,
            patterns=[
                "us_county+ co_label+ ,? us_state+",
            ],
        ),
        Compiler(
            label="county_state_iffy",
            id="admin_unit",
            on_match=act.COUNTY_STATE_IFFY_MATCH,
            decoder=decoder,
            patterns=[
                "us_county+ ,? us_state+",
            ],
        ),
        Compiler(
            label="county_only",
            id="admin_unit",
            on_match=act.COUNTY_ONLY_MATCH,
            decoder=decoder,
            patterns=[
                "us_county+ co_label+",
                "co_word :? us_county+",
            ],
        ),
        Compiler(
            label="state_county",
            id="admin_unit",
            on_match=act.STATE_COUNTY_MATCH,
            decoder=decoder,
            patterns=[
                "              us_state+ co_label* ,? us_county+ co_label*",
                "st_label+ of? us_state+ co_label+ ,? us_county+ co_label*",
            ],
        ),
        Compiler(
            label="state_only",
            id="admin_unit",
            on_match=act.STATE_ONLY_MATCH,
            decoder=decoder,
            patterns=[
                "st_label+ of? ,? us_state+",
            ],
        ),
    ]


def not_admin_unit():
    decoder = {
        "bad_prefix": {"ENT_TYPE": "bad_prefix"},
        "bad_suffix": {"ENT_TYPE": "bad_suffix"},
        "us_county": {"ENT_TYPE": {"IN": act.COUNTY_ENTS}},
        "us_state": {"ENT_TYPE": {"IN": act.STATE_ENTS}},
    }
    return [
        Compiler(
            label="not_admin_unit",
            on_match=reject_match.REJECT_MATCH,
            decoder=decoder,
            patterns=[
                "bad_prefix+ us_county+",
                "            us_county+ bad_suffix+",
                "bad_prefix+ us_county+ bad_suffix+",
                "bad_prefix+ us_state+",
                "            us_state+  bad_suffix+",
                "bad_prefix+ us_state+  bad_suffix+",
            ],
        ),
    ]
