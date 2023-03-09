from plants.pylib.pipeline_builder import PipelineBuilder
from traiter.pylib.pattern_compilers import matcher_compiler
from traiter.pylib.pipes.add_traits_pipe import ADD_TRAITS
from traiter.pylib.pipes.delete_traits_pipe import DELETE_TRAITS
from traiter.pylib.pipes.term_pipe import TERM_PIPE

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

    pipe.add_taxon_terms(before="ner")
    pipe.add_taxa_patterns(before="ner")
    pipe.add_taxon_plus_patterns(n=2, before="ner")

    # pipe.add_debug_tokens_pipe()  # ###############################################
    pipe.add_basic_terms(terms.TERMS1, before="ner")

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        name="lat_long_traits",
        before="ner",
        config={"patterns": matcher_compiler.as_dicts([lat_long_patterns.LAT_LONG])},
    )
    pipe.nlp.add_pipe("merge_entities", name="merge_lat_long", before="ner")

    pipe.add_habitat_patterns(before="ner")

    # Only keep the PERSON entities
    # We need to delete these entities because we merge entity tokens later in pipeline
    pipe.remove_spacy_ents(keep="PERSON", after="ner")

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        name="name_traits",
        after="delete_spacy",
        config={"patterns": matcher_compiler.as_dicts([name_patterns.NAME])},
    )
    pipe.nlp.add_pipe("merge_entities", name="merge_names")

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        config={
            "patterns": matcher_compiler.as_dicts(
                [
                    collector_patterns.COLLECTOR,
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
        name="delete_terms1",
        config={
            "delete": """ time_units month name col_label det_label job_label not_name
            no_label habitat_prefix habitat_suffix PERSON """.split()
        },
    )

    pipe.nlp.add_pipe(
        TERM_PIPE,
        name="terms2",
        config={
            "terms": terms.TERMS2,
            "replace": terms.REPLACE2,
        },
    )
    pipe.nlp.add_pipe("merge_entities", name="merge_terms2")

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

    pipe.nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_terms2",
        config={
            "delete": """ us_county us_state us_state-us_county time_units bad_taxon
            month name col_label det_label job_label not_name no_label
            higher_taxon lower_taxon
            """.split()
        },
    )

    for name in pipe.nlp.pipe_names:
        print(name)

    return pipe
