"""Create a trait pipeline."""
import spacy
from traiter.pipes.sentence import SENTENCE
from traiter.tokenizer_util import append_abbrevs
from traiter.tokenizer_util import append_tokenizer_regexes

from . import terms

# from traiter.patterns.matcher_patterns import add_ruler_patterns
# from traiter.pipes.simple_entity_data import SIMPLE_ENTITY_DATA

# from .. import consts
# from ..patterns.taxon_patterns import TAXON

# from traiter.pipes.debug import DEBUG_ENTITIES, DEBUG_TOKENS

# SIMPLE_DATA = [TAXON]


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

    nlp.add_pipe(SENTENCE, before="parser")

    # config = {"overwrite_ents": True}
    # match_ruler = nlp.add_pipe("entity_ruler", name="match_ruler", config=config)
    # add_ruler_patterns(match_ruler, SIMPLE_DATA)
    #
    # nlp.add_pipe(SIMPLE_ENTITY_DATA, config={"replace": consts.REPLACE})

    # nlp.add_pipe(DEBUG_TOKENS, config={'message': ''})
    # nlp.add_pipe(DEBUG_ENTITIES, config={'message': ''})

    return nlp
