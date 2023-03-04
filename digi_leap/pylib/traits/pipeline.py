from plants.pylib.pipeline_builder import PipelineBuilder
from traiter.pylib.pattern_compilers import matcher_compiler
from traiter.pylib.pipes.add_traits_pipe import ADD_TRAITS
from traiter.pylib.pipes.delete_traits_pipe import DELETE_TRAITS

from . import tokenizer
from .patterns import admin_unit_patterns
from .patterns import collector_patterns
from .patterns import determiner_patterns
from .patterns import label_date_patterns
from .patterns import lat_long_patterns
from .patterns import name_patterns
from .patterns import term_patterns as terms


def build_pipeline():
    pipe = PipelineBuilder(trained_pipeline="en_core_web_md")

    tokenizer.setup_tokenizer(pipe.nlp)
    pipe.add_term_patterns(terms.TERMS, terms.REPLACE)

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

    # pipe.add_debug_tokens_pipe()

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
        ADD_TRAITS,
        name="admin_unit_pipe",
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
            month name col_label det_label job_label lat_long not_name
            no_label """.split()
        },
    )

    return pipe
