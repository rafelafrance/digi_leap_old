from typing import Dict
from typing import List

from traiter.pylib.util import shorten

from digi_leap.pylib.traits import pipeline

NLP = pipeline.build_pipeline()  # Singleton for testing


def test(text: str) -> List[Dict]:
    text = shorten(text)

    doc = NLP(text)

    traits = [e._.data for e in doc.ents]

    # from pprint import pp
    # pp(traits, compact=True)

    return traits
