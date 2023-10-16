from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from spacy.language import Language
from spacy.util import registry
from traiter.pylib import const as t_const
from traiter.pylib import term_util
from traiter.pylib.pattern_compiler import Compiler
from traiter.pylib.pipes import add
from traiter.pylib.pipes import reject_match
from traiter.pylib.traits import terms as t_terms

from .base import Base

ADMIN_UNIT_CSV = Path(__file__).parent / "terms" / "admin_unit_terms.csv"
US_LOCATIONS_CSV = Path(t_terms.__file__).parent / "us_location_terms.csv"
OTHER_LOCATIONS_CSV = Path(t_terms.__file__).parent / "other_location_terms.csv"
ALL_CSVS = [US_LOCATIONS_CSV, ADMIN_UNIT_CSV, OTHER_LOCATIONS_CSV]

REPLACE = term_util.term_data(ALL_CSVS, "replace")
COUNTY_IN = term_util.term_data(ALL_CSVS, "inside")
POSTAL = term_util.term_data(ALL_CSVS, "postal")

STATE_ENTS = ["us_state", "us_state-us_county", "us_territory"]
COUNTY_ENTS = ["us_county", "us_state-us_county"]
ADMIN_ENTS = ["us_state", "us_county", "us_state-us_county", "us_territory"]


def build(nlp: Language, overwrite: Optional[list[str]] = None):
    add.term_pipe(nlp, name="admin_unit_terms", path=ALL_CSVS)

    add.trait_pipe(nlp, name="not_admin_unit", compiler=not_admin_unit())

    overwrite = overwrite if overwrite else []
    overwrite += """
        us_county us_state us_state-us_county us_territory
        county_label state_label country
        """.split()
    add.trait_pipe(
        nlp,
        name="admin_unit_patterns",
        compiler=admin_unit_patterns(),
        overwrite=overwrite,
    )

    add.cleanup_pipe(nlp, name="admin_unit_cleanup")


def admin_unit_patterns():
    decoder = {
        ",": {"TEXT": {"REGEX": r"^[:._;,]+$"}},
        ":": {"TEXT": {"IN": t_const.COLON}},
        "co_label": {"ENT_TYPE": "county_label"},
        "co_word": {"LOWER": {"IN": ["county"]}},
        "country": {"ENT_TYPE": "country"},
        "of": {"LOWER": {"IN": ["of"]}},
        "prov": {"ENT_TYPE": "province_label"},
        "sp": {"IS_SPACE": True},
        "st_label": {"ENT_TYPE": "state_label"},
        "us_county": {"ENT_TYPE": {"IN": COUNTY_ENTS}},
        "us_state": {"ENT_TYPE": {"IN": STATE_ENTS}},
        "word": {"IS_ALPHA": True},
    }
    return [
        Compiler(
            label="country",
            id="admin_unit",
            on_match="country_match",
            keep="country",
            decoder=decoder,
            patterns=[
                "country+",
            ],
        ),
        Compiler(
            label="county_state",
            id="admin_unit",
            on_match="county_state_match",
            keep="admin_unit",
            decoder=decoder,
            patterns=[
                "us_county+ co_label+ ,? sp? us_state+",
            ],
        ),
        Compiler(
            label="county_state_iffy",
            id="admin_unit",
            on_match="county_state_iffy_match",
            keep="admin_unit",
            decoder=decoder,
            patterns=[
                "us_county+ ,? sp? us_state+",
            ],
        ),
        Compiler(
            label="county_only",
            id="admin_unit",
            on_match="county_only_match",
            keep="admin_unit",
            decoder=decoder,
            patterns=[
                "us_county+ co_label+",
                "co_word :? us_county+",
            ],
        ),
        Compiler(
            label="state_county",
            id="admin_unit",
            on_match="state_county_match",
            keep="admin_unit",
            decoder=decoder,
            patterns=[
                "              us_state+ co_label* ,? sp? us_county+ co_label*",
                "st_label+ of? us_state+ co_label+ ,? sp? us_county+ co_label*",
            ],
        ),
        Compiler(
            label="state_only",
            id="admin_unit",
            on_match="state_only_match",
            keep="admin_unit",
            decoder=decoder,
            patterns=[
                "st_label+ of? ,? us_state+",
            ],
        ),
        Compiler(
            label="province",
            id="admin_unit",
            on_match="province_match",
            keep="admin_unit",
            decoder=decoder,
            patterns=[
                "prov+ word",
                "prov+ country",
            ],
        ),
    ]


def not_admin_unit():
    decoder = {
        "bad_prefix": {"ENT_TYPE": "bad_prefix"},
        "bad_suffix": {"ENT_TYPE": "bad_suffix"},
        "us_county": {"ENT_TYPE": {"IN": COUNTY_ENTS}},
        "us_state": {"ENT_TYPE": {"IN": STATE_ENTS}},
    }
    return [
        Compiler(
            label="not_admin_unit",
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


@dataclass()
class AdminUnit(Base):
    country: str = None
    province: str = None
    us_state: str = None
    us_county: str = None

    @classmethod
    def from_ent(cls, ent, **kwargs):
        trait = super().from_ent(ent, **kwargs)
        trait.trait = "admin_unit"
        return trait

    @classmethod
    def province_match(cls, ent):
        prov = []
        for token in ent:
            if token.ent_type_ != "province_label":
                prov.append(token.lower_)

        return cls.from_ent(ent, province=" ".join(prov))

    @classmethod
    def state_only_match(cls, ent):
        return cls.from_ent(ent, us_state=cls.format_state(ent, ent_index=0))

    @classmethod
    def country_match(cls, ent):
        country = REPLACE.get(ent.text.lower(), ent.text)
        return cls.from_ent(ent, country=country)

    @classmethod
    def county_state_match(cls, ent):
        if len(ent.ents) < 2:
            raise reject_match.RejectMatch

        return cls.from_ent(
            ent,
            us_state=cls.format_state(ent, ent_index=1),
            us_county=cls.format_county(ent, ent_index=0),
        )

    @classmethod
    def county_state_iffy_match(cls, ent):
        sub_ents = [
            e for e in ent.ents if e.label_ in [*ADMIN_ENTS, "county_label_iffy"]
        ]

        if len(sub_ents) < 2:
            raise reject_match.RejectMatch

        county_ent = sub_ents[0]
        state_ent = sub_ents[1]

        if cls.is_county_not_colorado(state_ent, county_ent):
            return cls.from_ent(ent, us_county=cls.format_county(ent, ent_index=0))

        elif not cls.county_in_state(state_ent, county_ent):
            raise reject_match.RejectMatch

        else:
            return cls.from_ent(
                ent,
                us_state=cls.format_state(ent, ent_index=1),
                us_county=cls.format_county(ent, ent_index=0),
            )

    @classmethod
    def county_only_match(cls, ent):
        return cls.from_ent(ent, us_county=cls.format_county(ent, ent_index=0))

    @classmethod
    def state_county_match(cls, ent):
        return cls.from_ent(
            ent,
            us_state=cls.format_state(ent, ent_index=0),
            us_county=cls.format_county(ent, ent_index=1),
        )

    @staticmethod
    def format_state(ent, *, ent_index: int):
        sub_ents = [e for e in ent.ents if e.label_ in ADMIN_ENTS]
        state = sub_ents[ent_index].text
        st_key = AdminUnit.get_state_key(state)
        return REPLACE.get(st_key, state)

    @staticmethod
    def format_county(ent, *, ent_index: int):
        sub_ents = [e.text for e in ent.ents if e.label_ in ADMIN_ENTS]
        return sub_ents[ent_index].title()

    @staticmethod
    def is_county_not_colorado(state_ent, county_ent):
        """Flag if Co = county label or CO = Colorado."""
        return state_ent.text == "CO" and county_ent.text.isupper()

    @staticmethod
    def get_state_key(state):
        return state.upper() if len(state) <= 2 else state.lower()

    @staticmethod
    def county_in_state(state_ent, county_ent):
        st_key = AdminUnit.get_state_key(state_ent.text)
        co_key = county_ent.text.lower()
        return POSTAL.get(st_key, "") in COUNTY_IN[co_key]


@registry.misc("province_match")
def province_match(ent):
    return AdminUnit.province_match(ent)


@registry.misc("state_only_match")
def state_only_match(ent):
    return AdminUnit.state_only_match(ent)


@registry.misc("country_match")
def country_match(ent):
    return AdminUnit.country_match(ent)


@registry.misc("county_state_match")
def county_state_match(ent):
    return AdminUnit.county_state_match(ent)


@registry.misc("county_state_iffy_match")
def county_state_iffy_match(ent):
    return AdminUnit.county_state_iffy_match(ent)


@registry.misc("county_only_match")
def county_only_match(ent):
    return AdminUnit.county_only_match(ent)


@registry.misc("state_county_match")
def state_county_match(ent):
    return AdminUnit.state_county_match(ent)
