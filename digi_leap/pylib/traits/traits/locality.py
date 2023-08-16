import os
from pathlib import Path

from spacy.language import Language
from spacy.util import registry
from traiter.pylib.pattern_compiler import Compiler
from traiter.pylib.pipes import add

USE_MOCK_DATA = 0

OTHER_TRAITS = " habitat color admin_unit ".split()


def get_csvs():
    global USE_MOCK_DATA

    here = Path(__file__).parent / "terms"
    csvs = [
        here / "locality_terms.zip",
        here / "not_locality_terms.csv",
    ]

    try:
        USE_MOCK_DATA = int(os.getenv("MOCK_DATA"))
    except (TypeError, ValueError):
        USE_MOCK_DATA = 0

    if not csvs[0].exists or USE_MOCK_DATA:
        csvs = [
            here / "mock_locality_terms.csv",
            here / "not_locality_terms.csv",
        ]

    return csvs


def build(nlp: Language):
    default_labels = {
        "locality_terms": "loc",
        "mock_locality_terms": "loc",
        "not_locality_terms": "not_loc",
    }
    add.term_pipe(
        nlp, name="locality_terms", path=get_csvs(), default_labels=default_labels
    )

    # add.debug_tokens(nlp)  # ##########################################

    add.trait_pipe(nlp, name="locality_patterns", compiler=locality_patterns())

    add.custom_pipe(nlp, registered="prune_localities")

    # add.debug_tokens(nlp)  # ##########################################

    for i in range(2):
        add.trait_pipe(
            nlp,
            name=f"extend_locality{i}",
            compiler=extend_locality(),
            overwrite=["locality", *OTHER_TRAITS],
        )

    # add.debug_tokens(nlp)  # ##########################################

    add.cleanup_pipe(nlp, name="locality_cleanup")


def locality_patterns():
    return [
        Compiler(
            label="locality",
            on_match="locality_match",
            keep="locality",
            decoder={
                "'s": {"POS": "PART"},
                "9": {"LIKE_NUM": True},
                "and": {"POS": {"IN": "ADP AUX CCONJ DET NUM PUNCT SCONJ".split()}},
                "loc": {"ENT_TYPE": "loc"},
                # "rt": {"LOWER": {"REGEX": r"^[a-z]\w+$"}},
            },
            patterns=[
                "9? loc 's?   loc+ 9?",
                "9? loc+ and+ loc+ 9?",
                "9? loc+ and+ loc+ and+ loc+ 9?",
                "9? loc+ and+ loc+ and+ loc+ and+ loc+ 9?",
                "9? loc+ and+ loc+ and+ loc+ and+ loc+ and+ loc+ 9?",
            ],
        )
    ]


def extend_locality():
    return [
        Compiler(
            label="locality",
            on_match="locality_match",
            keep="locality",
            decoder={
                ".": {"TEXT": "."},
                "/": {"TEXT": "/"},
                "9": {"LIKE_NUM": True},
                "trait": {"ENT_TYPE": {"IN": OTHER_TRAITS}},
                "locality": {"ENT_TYPE": "locality"},
                "in_sent": {"IS_SENT_START": False},
                "sent_start": {"IS_SENT_START": True},
                "word": {"IS_ALPHA": True},
            },
            patterns=[
                "locality+   in_sent+ locality+",
                "locality+   word?    trait* .",
                "sent_start+ 9? /?    locality+",
            ],
        )
    ]


@registry.misc("locality_match")
def locality_match(ent):
    ent._.data = {"locality": ent.text.lstrip("(")}


@Language.component("prune_localities")
def prune_localities(doc):
    if USE_MOCK_DATA:
        return doc

    ents = []
    add_locality = False

    for ent in doc.ents:
        trait = ent._.data["trait"]

        # Localities come after taxa
        if trait in ("taxon",):  # "admin_unit"):
            add_locality = True
            ents.append(ent)
        # Localities are before collector etc.
        elif trait in ("collector", "date", "determiner"):
            add_locality = False
            ents.append(ent)
        elif trait == "locality" and not add_locality:
            continue
        else:
            ents.append(ent)

    doc.set_ents(sorted(ents, key=lambda e: e.start))
    return doc
