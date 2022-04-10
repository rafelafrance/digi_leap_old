"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.cleanup import CLEANUP
from traiter.pipes.merge_entity_data import MERGE_ENTITY_DATA
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

from . import pipeline_utils
from ..patterns import admin_unit_patterns
from ..patterns import forget_patterns
from ..patterns import taxon_patterns
from ..patterns import terms


def build_pipeline():
    nlp = spacy.load("en_core_web_md", exclude=["ner"])

    pipeline_utils.setup_tokenizer(nlp)
    pipeline_utils.setup_term_pipe(nlp, terms.VOCAB_TERMS)

    nlp.add_pipe("merge_entities", name="term_merger", after="parser")
    nlp.add_pipe(SIMPLE_ENTITY_DATA)

    nlp.add_pipe(
        MERGE_ENTITY_DATA,
        config={
            "patterns": matcher_patterns.as_dicts(
                [
                    admin_unit_patterns.COUNTY_BEFORE_STATE,
                    admin_unit_patterns.COUNTY_ONLY,
                    admin_unit_patterns.STATE_BEFORE_COUNTY,
                    admin_unit_patterns.STATE_ONLY,
                    taxon_patterns.TAXON,
                ]
            )
        },
    )

    # pipeline_utils.debug_tokens(nlp)

    nlp.add_pipe(CLEANUP, config={"forget": forget_patterns.ALL_ENTITIES})

    return nlp
