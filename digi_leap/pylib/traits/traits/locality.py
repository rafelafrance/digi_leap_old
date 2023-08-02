import os
from pathlib import Path

from spacy.language import Language
from spacy.util import registry
from traiter.pylib.pattern_compiler import Compiler
from traiter.pylib.pipes import add


def get_csv():
    here = Path(__file__).parent / "terms"
    csv_ = here / "locality_terms.zip"

    try:
        use_mock_data = int(os.getenv("MOCK_DATA"))
    except (TypeError, ValueError):
        use_mock_data = 0

    if not csv_.exists or use_mock_data:
        csv_ = here / "mock_locality_terms.csv"

    return csv_


RT_RE = r"^[a-z]\w+$"

LOC_POS = "CCONJ SCONJ DET ADP NUM PUNCT".split()


def build(nlp: Language):
    default_labels = {
        "locality_terms": "locality",
        "mock_locality_terms": "locality",
    }
    add.term_pipe(
        nlp, name="locality_terms", path=get_csv(), default_labels=default_labels
    )

    # add.debug_tokens(nlp)  # ##########################################

    add.trait_pipe(
        nlp,
        name="locality_patterns",
        compiler=locality_patterns(),
    )

    # add.debug_tokens(nlp)  # ##########################################


def locality_patterns():
    return [
        Compiler(
            label="locality",
            on_match="locality_match",
            decoder={
                ",": {"IS_PUNCT": True},
                "9": {"LIKE_NUM": True},
                "and": {"POS": {"IN": LOC_POS}},
                "loc": {"ENT_TYPE": "locality"},
                "rt": {"LOWER": {"REGEX": RT_RE}},
            },
            patterns=[
                "9? loc+ 9?",
                "9? loc+ and+ loc+ 9?",
                "9? loc+ and+ loc+ and+ loc+ 9?",
                "9? loc+ and+ loc+ and+ loc+ and+ loc+ 9?",
                "9? loc+ and+ loc+ and+ loc+ and+ loc+ and+ loc+ 9?",
            ],
        )
    ]


@registry.misc("locality_match")
def locality_match(ent):
    ent._.data = {"locality": ent.text}
