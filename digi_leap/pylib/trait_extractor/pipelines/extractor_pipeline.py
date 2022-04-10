"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.add_entities import ADD_ENTITIES

from . import pipeline_utils
from ..patterns import collector_patterns
from ..patterns import determiner_patterns
from ..patterns import forget_patterns
from ..patterns import label_date_patterns
from ..patterns import name_patterns
from ..patterns import terms


def build_pipeline():
    nlp = spacy.load("en_core_web_md", disable=["senter"])

    pipeline_utils.setup_tokenizer(nlp)

    pipeline_utils.setup_term_pipe(nlp, terms.ExtractorTerms.terms)

    # We only want the PERSON
    forget = forget_patterns.spacy_entities()
    forget.remove("PERSON")
    pipeline_utils.forget_entities(nlp, forget=forget, name="forget_spacy_entities")

    # Build up names from PERSON entities
    nlp.add_pipe(
        ADD_ENTITIES,
        name="name_entities",
        config={
            "patterns": matcher_patterns.as_dicts([name_patterns.build_name_patterns()])
        },
    )
    nlp.add_pipe("merge_entities", name="name_merger")

    nlp.add_pipe(
        ADD_ENTITIES,
        name="extractor_entities",
        config={
            "patterns": matcher_patterns.as_dicts(
                [
                    collector_patterns.build_collector_patterns(),
                    determiner_patterns.build_determiner_patterns(),
                    label_date_patterns.build_label_date_patterns(),
                    label_date_patterns.build_missing_day_patterns(),
                ]
            )
        },
    )

    # pipeline_utils.debug_tokens(nlp)

    pipeline_utils.forget_entities(nlp)

    return nlp
