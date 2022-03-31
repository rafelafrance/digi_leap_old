"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.add_entity_data import ADD_ENTITY_DATA
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

from . import pipeline_utils
from ..patterns import collector_patterns
from ..patterns import forget_patterns
from ..patterns import label_date_patterns
from ..terms import extractor_terms


ADD_DATA = [
    label_date_patterns.LABEL_DATE,
    label_date_patterns.SHORT_DATE,
    collector_patterns.COLLECTOR,
]


def pipeline():
    """Create a pipeline for extracting traits."""
    nlp = spacy.load("en_core_web_md")

    pipeline_utils.setup_term_pipe(nlp, extractor_terms.TERMS)

    forget = forget_patterns.FORGET_SPACY
    forget.remove("PERSON")
    pipeline_utils.forget_entities(
        nlp,
        forget=forget,
        name="clean_spacy",
        after="ner",
    )

    nlp.add_pipe("merge_entities", name="term_merger", after="clean_spacy")
    nlp.add_pipe(SIMPLE_ENTITY_DATA, after="term_merger")

    match_ruler = nlp.add_pipe(
        "entity_ruler", name="match_ruler", config={"overwrite_ents": True}
    )
    matcher_patterns.add_ruler_patterns(match_ruler, ADD_DATA)

    nlp.add_pipe(
        ADD_ENTITY_DATA,
        config={"dispatch": matcher_patterns.patterns_to_dispatch(ADD_DATA)},
    )

    # pipeline_utils.debug_tokens(nlp, name="extractor_pipe")

    pipeline_utils.forget_entities(nlp)

    return nlp
