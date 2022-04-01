"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.add_entity_data import ADD_ENTITY_DATA
from traiter.pipes.cache import CACHE_LABEL
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

from . import pipeline_utils
from ..patterns import collector_patterns
from ..patterns import forget_patterns
from ..patterns import label_date_patterns
from ..patterns import name_patterns
from ..patterns.terms import ExtractorTerms


ADD_DATA = [
    label_date_patterns.build_label_date_patterns(),
    label_date_patterns.build_missing_day_patterns(),
    collector_patterns.build_collector_patterns(),
]

NAME_DATA = [name_patterns.build_name_patterns()]


def pipeline():
    """Create a pipeline for extracting traits."""
    nlp = spacy.load("en_core_web_md", disable=["senter"])

    pipeline_utils.setup_term_pipe(nlp, ExtractorTerms.terms)

    # We only want the PERSON entities for now
    forget = forget_patterns.spacy_entities()
    forget.remove("PERSON")
    pipeline_utils.forget_entities(
        nlp,
        forget=forget,
        name="clean_spacy",
        after="ner",
    )

    # Merge the entities
    nlp.add_pipe("merge_entities", name="term_merger", after="clean_spacy")
    nlp.add_pipe(SIMPLE_ENTITY_DATA, name="term_data", after="term_merger")

    # Build names before finding patterns that depend on names
    name_matcher = nlp.add_pipe(
        "entity_ruler",
        name="name_matcher",
        after="term_data",
        config={"overwrite_ents": True},
    )
    matcher_patterns.compile_ruler_patterns(name_matcher, NAME_DATA)
    nlp.add_pipe(CACHE_LABEL, name="name_cache", after="name_matcher")
    nlp.add_pipe(
        ADD_ENTITY_DATA,
        name="name_data",
        after="name_cache",
        config={"dispatch": matcher_patterns.patterns_to_dispatch(NAME_DATA)},
    )
    nlp.add_pipe("merge_entities", name="name_merger", after="name_data")

    # Normal patterns
    extractor_matcher = nlp.add_pipe(
        "entity_ruler",
        name="extractor_matcher",
        after="name_merger",
        config={"overwrite_ents": True},
    )
    matcher_patterns.compile_ruler_patterns(extractor_matcher, ADD_DATA)
    nlp.add_pipe(
        ADD_ENTITY_DATA,
        name="extractor_data",
        after="extractor_matcher",
        config={"dispatch": matcher_patterns.patterns_to_dispatch(ADD_DATA)},
    )

    pipeline_utils.forget_entities(nlp)

    return nlp
