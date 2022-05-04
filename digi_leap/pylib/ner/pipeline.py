import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.add_traits_pipe import ADD_TRAITS
from traiter.pipes.delete_traits_pipe import DELETE_TRAITS
from traiter.pipes.simple_traits_pipe import SIMPLE_TRAITS
from traiter.pipes.term_pipe import TERM_PIPE

from . import tokenizer
from .patterns import admin_unit_patterns
from .patterns import collector_patterns
from .patterns import determiner_patterns
from .patterns import label_date_patterns
from .patterns import lat_long_patterns
from .patterns import name_patterns
from .patterns import taxon_patterns
from .patterns import term_utils

# from traiter.pipes import debug_pipes


def build_pipeline():
    nlp = spacy.load("en_core_web_md", disable=["senter"])

    tokenizer.setup_tokenizer(nlp)

    nlp.add_pipe(
        TERM_PIPE,
        name="extractor_terms",
        before="parser",
        config={
            "terms": term_utils.EXTRACTOR_TERMS.terms,
            "replace": term_utils.REPLACE,
        },
    )

    # We only want the PERSON entity from spacy
    nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_spacy",
        config={
            "delete": """ CARDINAL DATE EVENT FAC GPE LANGUAGE LAW LOC MONEY NORP
            ORDINAL ORG PERCENT PRODUCT QUANTITY TIME WORK_OF_ART not_name """.split()
        },
    )

    # Build up names from PERSON entities
    # debug_pipes.tokens(nlp)  # ######################################################
    nlp.add_pipe(
        ADD_TRAITS,
        name="name_traits",
        config={
            "patterns": matcher_patterns.as_dicts(
                [
                    name_patterns.NAME,
                    lat_long_patterns.LAT_LONG,
                ]
            )
        },
    )

    # debug_pipes.tokens(nlp)  # ######################################################
    nlp.add_pipe(
        ADD_TRAITS,
        config={
            "patterns": matcher_patterns.as_dicts(
                [
                    collector_patterns.COLLECTOR,
                    collector_patterns.NOT_COLLECTOR,
                    determiner_patterns.DETERMINER,
                    label_date_patterns.LABEL_DATE,
                    label_date_patterns.MISSING_DAY,
                ]
            ),
            "keep": ["lat_long"],
        },
    )

    nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_extracts",
        config={"delete": """ month time_units name """.split()},
    )

    nlp.add_pipe(
        TERM_PIPE,
        name="vocab_terms",
        config={"terms": term_utils.VOCAB_TERMS.terms, "replace": term_utils.REPLACE},
    )

    nlp.add_pipe("merge_entities", name="merge_vocab")

    nlp.add_pipe(
        SIMPLE_TRAITS,
        config={
            "update": """ level plant_taxon us_county us_state us_state-us_county
                us_territory""".split()
        },
    )

    nlp.add_pipe(
        ADD_TRAITS,
        name="admin_unit_traits",
        config={
            "patterns": matcher_patterns.as_dicts(
                [
                    admin_unit_patterns.COUNTY_STATE,
                    admin_unit_patterns.COUNTY_STATE_IFFY,
                    admin_unit_patterns.COUNTY_ONLY,
                    admin_unit_patterns.STATE_COUNTY,
                    admin_unit_patterns.STATE_ONLY,
                ]
            ),
        },
    )

    nlp.add_pipe(
        ADD_TRAITS,
        name="taxon_traits",
        config={
            "patterns": matcher_patterns.as_dicts([taxon_patterns.TAXON]),
            "keep": """ admin_unit collector determiner label_date """.split(),
        },
    )

    nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_vocab",
        config={
            "delete": """ us_county us_state us_state-us_county time_units
            month name plant_taxon col_label det_label job_label level lat_long
            no_label """.split()
        },
    )

    return nlp
