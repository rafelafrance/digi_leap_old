"""Create a trait pipeline."""
import spacy
from traiter import tokenizer_util
from traiter.patterns import matcher_patterns
from traiter.pipes.add_entity_data import ADD_ENTITY_DATA
from traiter.pipes.cleanup import CLEANUP
from traiter.pipes.merge_entity_data import MERGE_ENTITY_DATA
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

from .. import terms
from ..patterns import admin_unit_patterns
from ..patterns import forget_patterns
from ..patterns import label_date_patterns

# from traiter.pipes.debug import DEBUG_ENTITIES, DEBUG_TOKENS


ADD_DATA = [
    label_date_patterns.LABEL_DATE,
    label_date_patterns.SHORT_DATE,
]

INFIX = [
    r"(?<=[0-9])[/,](?=[0-9])",  # digit,digit
    r"(?<=[A-Z])[/-](?=[0-9])",  # letter-digit
    "-_",
]


def pipeline():
    """Create a pipeline for extracting traits."""
    nlp = spacy.load("en_core_web_sm", exclude=["ner"])

    tokenizer_util.append_prefix_regex(nlp)
    tokenizer_util.append_infix_regex(nlp, INFIX)
    tokenizer_util.append_suffix_regex(nlp)
    tokenizer_util.append_abbrevs(nlp, terms.ABBREVS)

    term_ruler = nlp.add_pipe(
        "entity_ruler",
        name="term_ruler",
        before="parser",
        config={"phrase_matcher_attr": "LOWER"},
    )
    term_ruler.add_patterns(terms.TERMS.for_entity_ruler())

    nlp.add_pipe("merge_entities", name="term_merger")
    nlp.add_pipe(SIMPLE_ENTITY_DATA, after="term_merger")

    match_ruler = nlp.add_pipe(
        "entity_ruler", name="match_ruler", config={"overwrite_ents": True}
    )
    matcher_patterns.add_ruler_patterns(match_ruler, ADD_DATA)

    nlp.add_pipe(
        ADD_ENTITY_DATA,
        config={"dispatch": matcher_patterns.patterns_to_dispatch(ADD_DATA)},
    )

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

    # nlp.add_pipe(DEBUG_TOKENS)
    # nlp.add_pipe(DEBUG_ENTITIES)

    nlp.add_pipe(CLEANUP, config={"forget": forget_patterns.FORGET})

    return nlp
