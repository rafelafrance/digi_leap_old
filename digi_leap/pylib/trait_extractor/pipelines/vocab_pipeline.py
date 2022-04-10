"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.merge_entity_data import MERGE_ENTITY_DATA
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

from . import pipeline_utils
from ..patterns import admin_unit_patterns
from ..patterns import taxon_patterns
from ..patterns import terms


def build_pipeline(load_patterns=None, save_patterns=None):
    nlp = spacy.load("en_core_web_md", exclude=["ner"])

    pipeline_utils.setup_tokenizer(nlp)

    term_ruler = terms.VocabTerms()
    if load_patterns:
        term_ruler.load_terms(nlp, load_patterns)
    else:
        term_ruler.build_terms(nlp)

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
                    taxon_patterns.build_taxon_patterns(),
                ]
            )
        },
    )

    # pipeline_utils.debug_tokens(nlp)

    pipeline_utils.forget_entities(nlp)

    if save_patterns:
        term_ruler.save_terms(save_patterns)

    return nlp
