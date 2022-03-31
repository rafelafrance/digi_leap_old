"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.merge_entity_data import MERGE_ENTITY_DATA
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

from . import pipeline_utils
from ..patterns import admin_unit_patterns
from ..terms import admin_unit_terms


def pipeline():
    """Create a pipeline for extracting traits."""
    nlp = spacy.load("en_core_web_md", exclude=["ner"])

    pipeline_utils.setup_term_pipe(nlp, admin_unit_terms.TERMS)

    nlp.add_pipe("merge_entities", name="term_merger", after="parser")
    nlp.add_pipe(SIMPLE_ENTITY_DATA, after="term_merger")

    nlp.add_pipe(
        MERGE_ENTITY_DATA,
        config={
            "patterns": matcher_patterns.as_dicts(
                [
                    admin_unit_patterns.STATE_BEFORE_COUNTY,
                    admin_unit_patterns.COUNTY_BEFORE_STATE,
                    admin_unit_patterns.COUNTY_ONLY,
                    admin_unit_patterns.STATE_ONLY,
                ]
            )
        },
    )

    # pipeline_utils.debug_tokens(nlp, name="admin_unit_pipe")

    pipeline_utils.forget_entities(nlp)

    return nlp
