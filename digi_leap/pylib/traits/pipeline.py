from plants.pylib.pipeline_builder import PipelineBuilder
from traiter.pylib.pattern_compilers import matcher_compiler
from traiter.pylib.pipes.add_traits_pipe import ADD_TRAITS
from traiter.pylib.pipes.delete_traits_pipe import DELETE_TRAITS
from traiter.pylib.pipes.simple_traits_pipe import SIMPLE_TRAITS
from traiter.pylib.pipes.term_pipe import TERM_PIPE

from . import tokenizer
from .patterns import admin_unit_patterns
from .patterns import collector_patterns
from .patterns import delete_patterns
from .patterns import determiner_patterns
from .patterns import label_date_patterns
from .patterns import lat_long_patterns
from .patterns import name_patterns
from .patterns import term_patterns


def build_pipeline():
    pipe = PipelineBuilder(trained_pipeline="en_core_web_md")

    tokenizer.setup_tokenizer(pipe.nlp)

    pipe.nlp.add_pipe(
        TERM_PIPE,
        name="extractor_terms",
        before="parser",
        config={
            "terms": term_patterns.EXTRACTOR_TERMS.terms,
            "replace": term_patterns.REPLACE,
        },
    )

    # We only want the PERSON entity from spacy
    pipe.nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_spacy",
        config={"delete": delete_patterns.UNUSED},
    )

    # Build up names from PERSON entities
    pipe.nlp.add_pipe(
        ADD_TRAITS,
        name="name_traits",
        config={
            "patterns": matcher_compiler.as_dicts(
                [
                    name_patterns.NAME,
                    lat_long_patterns.LAT_LONG,
                ]
            )
        },
    )

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        config={
            "patterns": matcher_compiler.as_dicts(
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

    pipe.nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_extracts",
        config={"delete": """ month time_units name """.split()},
    )

    pipe.nlp.add_pipe(
        TERM_PIPE,
        name="vocab_terms",
        config={
            "terms": term_patterns.VOCAB_TERMS.terms,
            "replace": term_patterns.REPLACE,
        },
    )

    pipe.nlp.add_pipe("merge_entities", name="merge_vocab")

    pipe.nlp.add_pipe(
        SIMPLE_TRAITS,
        config={
            "update": """ level plant_taxon us_county us_state us_state-us_county
                us_territory """.split()
        },
    )

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        name="admin_unit_traits",
        config={
            "patterns": matcher_compiler.as_dicts(
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

    pipe.add_taxa_patterns()
    pipe.add_taxon_plus_patterns()

    pipe.nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_vocab",
        config={
            "delete": """ us_county us_state us_state-us_county time_units
            month name plant_taxon col_label det_label job_label level lat_long
            no_label """.split()
        },
    )

    return pipe
