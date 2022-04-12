"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.add_traits import ADD_TRAITS
from traiter.pipes.delete_traits import DELETE_TRAITS
from traiter.pipes.simple_traits import SIMPLE_TRAITS

from ..patterns import admin_unit_patterns
from ..patterns import delete_patterns
from ..patterns import taxon_patterns
from ..patterns import term_utils

# from traiter.pipes import debug_traits


def build_pipeline():
    nlp = spacy.load("en_core_web_md", exclude=["ner"])

    term_utils.setup_tokenizer(nlp)
    term_utils.setup_term_pipe(nlp, term_utils.VOCAB_TERMS)

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

    # debug_traits.tokens(nlp)

    nlp.add_pipe(DELETE_TRAITS, config={"delete": delete_patterns.PARTIAL_TRAITS})

    return nlp
