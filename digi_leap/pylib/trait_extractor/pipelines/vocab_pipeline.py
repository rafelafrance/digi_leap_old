"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.add_traits import ADD_TRAITS
from traiter.pipes.forget_traits import FORGET_TRAITS
from traiter.pipes.simple_trait import SIMPLE_TRAITS

from . import pipeline_utils
from ..patterns import admin_unit_patterns
from ..patterns import forget_patterns
from ..patterns import taxon_patterns
from ..patterns import terms


def build_pipeline():
    nlp = spacy.load("en_core_web_md", exclude=["ner"])

    pipeline_utils.setup_tokenizer(nlp)
    pipeline_utils.setup_term_pipe(nlp, terms.VOCAB_TERMS)

    nlp.add_pipe("merge_entities", after="parser")
    nlp.add_pipe(SIMPLE_TRAITS)

    nlp.add_pipe(
        ADD_TRAITS,
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

    nlp.add_pipe(FORGET_TRAITS, config={"forget": forget_patterns.PARTIAL_TRAITS})

    return nlp
