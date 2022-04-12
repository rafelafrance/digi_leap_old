"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.add_traits_pipe import ADD_TRAITS
from traiter.pipes.delete_traits_pipe import DELETE_TRAITS

from ..patterns import collector_patterns
from ..patterns import delete_patterns
from ..patterns import determiner_patterns
from ..patterns import label_date_patterns
from ..patterns import name_patterns
from ..patterns import term_utils

# from traiter.pipes import debug_traits


def build_pipeline():
    nlp = spacy.load("en_core_web_md", disable=["senter"])

    term_utils.setup_tokenizer(nlp)

    term_utils.setup_term_pipe(nlp, term_utils.EXTRACTOR_TERMS)

    # We only want the PERSON entity from spacy
    nlp.add_pipe(
        DELETE_TRAITS,
        name="delete_spacy",
        config={"delete": delete_patterns.SPACY_ENTITIES},
    )

    # Build up names from PERSON entities
    nlp.add_pipe(
        ADD_TRAITS,
        name="name_traits",
        config={"patterns": matcher_patterns.as_dicts([name_patterns.NAME])},
    )
    nlp.add_pipe("merge_entities")  # We want name to be a single token trait

    # Build the rest of the entities
    nlp.add_pipe(
        ADD_TRAITS,
        config={
            "patterns": matcher_patterns.as_dicts(
                [
                    collector_patterns.COLLECTOR,
                    determiner_patterns.DETERMINER,
                    label_date_patterns.LABEL_DATE,
                    label_date_patterns.MISSING_DAY,
                ]
            )
        },
    )

    # debug_traits.tokens(nlp)

    nlp.add_pipe(DELETE_TRAITS, config={"delete": delete_patterns.PARTIAL_TRAITS})

    return nlp
