"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.merge_entity_data import MERGE_ENTITY_DATA
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

from . import pipeline_utils
from ..patterns import admin_unit_patterns
from ..patterns.terms import AdminUnitTerms


def pipeline():
    """Create a pipeline for extracting traits."""
    nlp = spacy.load("en_core_web_md", exclude=["ner"])

    pipeline_utils.setup_term_pipe(nlp, AdminUnitTerms.terms)

    nlp.add_pipe("merge_entities", name="term_merger", after="parser")
    nlp.add_pipe(SIMPLE_ENTITY_DATA, after="term_merger")

    nlp.add_pipe(
        MERGE_ENTITY_DATA,
        config={
            "patterns": matcher_patterns.as_dicts(
                [
                    admin_unit_patterns.build_county_before_state_patterns(),
                    admin_unit_patterns.build_county_only_patterns(),
                    admin_unit_patterns.build_state_before_county_patterns(),
                    admin_unit_patterns.build_state_only_patterns(),
                ]
            )
        },
    )

    # pipeline_utils.debug_tokens(nlp, name="admin_unit_pipe")

    pipeline_utils.forget_entities(nlp)

    return nlp
