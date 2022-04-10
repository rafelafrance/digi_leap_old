"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.add_entity_data import ADD_ENTITY_DATA
from traiter.pipes.cache import CACHE_LABEL
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

from . import pipeline_utils
from ..patterns import collector_patterns
from ..patterns import determiner_patterns
from ..patterns import forget_patterns
from ..patterns import label_date_patterns
from ..patterns import name_patterns
from ..patterns import terms


def build_pipeline(load_patterns=None, save_patterns=None):
    nlp = spacy.load("en_core_web_md", disable=["senter"])

    pipeline_utils.setup_tokenizer(nlp)

    term_ruler = terms.ExtractorTerms()
    if load_patterns:
        term_ruler.load_terms(nlp, load_patterns)
    else:
        term_ruler.build_terms(nlp)

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
    name_data = [name_patterns.build_name_patterns()]
    matcher_patterns.compile_ruler_patterns(name_matcher, name_data)

    nlp.add_pipe(CACHE_LABEL, name="name_cache", after="name_matcher")
    nlp.add_pipe(
        ADD_ENTITY_DATA,
        name="name_data",
        after="name_cache",
        config={"dispatch": matcher_patterns.patterns_to_dispatch(name_data)},
    )
    nlp.add_pipe("merge_entities", name="name_merger", after="name_data")

    # Normal patterns
    extractor_matcher = nlp.add_pipe(
        "entity_ruler",
        name="extractor_matcher",
        after="name_merger",
        config={"overwrite_ents": True},
    )
    add_data = [
        label_date_patterns.build_label_date_patterns(),
        label_date_patterns.build_missing_day_patterns(),
        collector_patterns.build_collector_patterns(),
        determiner_patterns.build_determiner_patterns(),
    ]
    matcher_patterns.compile_ruler_patterns(extractor_matcher, add_data)

    nlp.add_pipe(
        ADD_ENTITY_DATA,
        name="extractor_data",
        after="extractor_matcher",
        config={"dispatch": matcher_patterns.patterns_to_dispatch(add_data)},
    )

    # pipeline_utils.debug_tokens(nlp)

    pipeline_utils.forget_entities(nlp)

    if save_patterns:
        term_ruler.save_terms(save_patterns)
        name_matcher.to_disk(save_patterns / "name_matcher.jsonl")
        extractor_matcher.to_disk(save_patterns / "extractor_matcher.jsonl")

    return nlp
