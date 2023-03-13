from plants.pylib.patterns.delete_patterns import PARTIAL_TRAITS
from plants.pylib.pipeline_builder import PipelineBuilder
from traiter.pylib.pattern_compilers import matcher_compiler
from traiter.pylib.pipes.add_traits_pipe import ADD_TRAITS
from traiter.pylib.pipes.delete_traits_pipe import DELETE_TRAITS
from traiter.pylib.pipes.term_pipe import TERM_PIPE

from . import tokenizer
from .patterns import admin_unit_patterns
from .patterns import associated_taxa_patterns
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

    pipe.add_basic_terms(terms.BASIC_TERMS, before="ner")

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        name="lat_long_traits",
        before="ner",
        config={"patterns": matcher_compiler.as_dicts([lat_long_patterns.LAT_LONG])},
    )
    pipe.nlp.add_pipe("merge_entities", name="lat_long_merge_traits", before="ner")

    pipe.add_habitat_patterns(before="ner")

    # Only keep the PERSON entities
    # We need to delete these entities because we merge entity tokens later in pipeline
    pipe.remove_spacy_ents(keep="PERSON", after="ner")

    # pipe.add_debug_tokens_pipe()  # ###############################################

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        name="name_traits",
        after="delete_spacy",
        config={"patterns": matcher_compiler.as_dicts([name_patterns.NAME])},
    )
    pipe.nlp.add_pipe("merge_entities", name="name_traits_merge")

    # pipe.add_debug_tokens_pipe()  # ###############################################

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        name="date_terms",
        config={
            "patterns": matcher_compiler.as_dicts(
                [
                    label_date_patterns.LABEL_DATE,
                    label_date_patterns.MISSING_DAY,
                ]
            ),
        },
    )

    pipe.nlp.add_pipe(
        ADD_TRAITS,
        name="label_terms",
        config={
            "patterns": matcher_compiler.as_dicts(
                [
                    collector_patterns.COLLECTOR,
                    collector_patterns.NOT_A_COLLECTOR,
                    determiner_patterns.DETERMINER,
                    associated_taxa_patterns.ASSOC_TAXA,
                ]
            ),
        },
    )

    pipe.nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_partial_terms",
        config={
            "delete": """ time_units month name col_label det_label job_label not_name
            no_label habitat_prefix habitat_suffix PERSON """.split()
        },
    )

    pipe.nlp.add_pipe(
        TERM_PIPE,
        name="location_terms",
        config={
            "terms": terms.LOCATION_TERMS,
            "replace": terms.REPLACE_LOCATION_TERMS,
        },
    )
    pipe.nlp.add_pipe("merge_entities", name="location_terms_merge")

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
    pipe.add_taxon_plus_patterns(n=2)

    pipe.nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_unused_terms",
        config={
            "delete": PARTIAL_TRAITS
            + """ us_county us_state us_state-us_county
                time_units bad_taxon month name col_label det_label job_label
                not_name no_label """.split()
        },
    )

    return pipe
