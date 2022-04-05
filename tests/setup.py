"""Setup for all tests."""
from typing import Dict
from typing import List

from traiter.util import shorten

from digi_leap.pylib.trait_extractor.pipelines import extractor_pipeline
from digi_leap.pylib.trait_extractor.pipelines import vocab_pipeline

NLP_EXTRACTOR = extractor_pipeline.pipeline()  # Singleton for testing
NLP_VOCAB = vocab_pipeline.pipeline()  # Singleton for testing


def test(text: str) -> List[Dict]:
    """Find entities in the doc."""
    text = shorten(text)

    extractor_doc = NLP_EXTRACTOR(text)
    admin_unit_doc = NLP_VOCAB(text)

    traits = [e._.data for e in extractor_doc.ents]
    traits += [e._.data for e in admin_unit_doc.ents]

    # from pprint import pp
    # pp(traits, compact=True)

    # from spacy import displacy
    # displacy.serve(doc, options={'collapse_punct': False, 'compact': True})

    return traits
