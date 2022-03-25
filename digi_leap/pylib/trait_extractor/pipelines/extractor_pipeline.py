"""Create a trait pipeline."""
import spacy
from traiter.patterns import matcher_patterns
from traiter.pipes.cleanup import CLEANUP
from traiter.pipes.merge_entity_data import MERGE_ENTITY_DATA
from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA
from traiter.tokenizer_util import append_abbrevs
from traiter.tokenizer_util import append_tokenizer_regexes

from .. import terms
from ..patterns import admin_unit_patterns
from ..patterns import forget_patterns

# from traiter.pipes.debug import DEBUG_ENTITIES, DEBUG_TOKENS


def pipeline():
    """Create a pipeline for extracting traits."""
    nlp = spacy.load("en_core_web_sm", exclude=["ner"])

    append_tokenizer_regexes(nlp)
    append_abbrevs(nlp, terms.ABBREVS)

    config = {"phrase_matcher_attr": "LOWER"}
    term_ruler = nlp.add_pipe(
        "entity_ruler", name="term_ruler", config=config, before="parser"
    )
    term_ruler.add_patterns(terms.TERMS.for_entity_ruler())

    nlp.add_pipe("merge_entities", name="term_merger")
    nlp.add_pipe(SIMPLE_ENTITY_DATA, after="term_merger")

    # config = {'overwrite_ents': True}
    # match_ruler = nlp.add_pipe('entity_ruler', name='match_ruler', config=config)
    # matcher_patterns.add_ruler_patterns(match_ruler, [
    #     admin_unit_patterns.ADMIN_UNIT,
    # ])

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
