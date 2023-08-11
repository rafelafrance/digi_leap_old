import os
from pathlib import Path

from spacy.language import Language
from spacy.util import registry
from traiter.pylib.pattern_compiler import Compiler
from traiter.pylib.pipes import add

USE_MOCK_DATA = 0

LOC_POS = "ADP AUX CCONJ DET NUM PUNCT SCONJ".split()
RT_RE = r"^[a-z]\w+$"

DECODER = {
    ",": {"IS_PUNCT": True},
    ".": {"TEXT": "."},
    "9": {"LIKE_NUM": True},
    "and": {"POS": {"IN": LOC_POS}},
    "habitat": {"ENT_TYPE": "habitat"},
    "loc": {"ENT_TYPE": "loc"},
    "locality": {"ENT_TYPE": "locality"},
    "rt": {"LOWER": {"REGEX": RT_RE}},
}


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

    # add.trait_pipe(
    #     nlp, name="not_locality_patterns", compiler=not_locality_patterns()
    # )

    add.trait_pipe(nlp, name="locality_patterns", compiler=locality_patterns())

    add.custom_pipe(nlp, registered="prune_localities")

    add.trait_pipe(
        nlp,
        name="extend_locality",
        compiler=locality_patterns(),
        overwrite=["habitat"],
    )

    # add.debug_tokens(nlp)  # ##########################################

    add.cleanup_pipe(nlp, name="locality_cleanup")


# def not_locality_patterns():
#     return [
#         Compiler(
#             label="not_locality",
#             decoder=DECODER,
#             patterns=[
#                 "nope+",
#             ],
#         ),
#     ]


def locality_patterns():
    return [
        Compiler(
            label="locality",
            on_match="locality_match",
            keep="locality",
            decoder=DECODER,
            patterns=[
                "9? loc loc+ 9?",
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
            decoder=DECODER,
            patterns=[
                "locality habitat* ,+ habitat* locality",
                "locality habitat+ .",
            ],
        )
    ]


@registry.misc("locality_match")
def locality_match(ent):
    ent._.data = {"locality": ent.text}


@Language.component("prune_localities")
def prune_localities(doc):
    if USE_MOCK_DATA:
        return doc

    ents = []
    add_locality = False

    for ent in doc.ents:
        trait = ent._.data["trait"]

        if trait in ("taxon",):  # "admin_unit"):
            add_locality = True
            ents.append(ent)
        elif trait in ("collector", "date", "determiner"):
            add_locality = False
            ents.append(ent)
        elif trait == "locality" and not add_locality:
            pass
        else:
            ents.append(ent)

    doc.set_ents(sorted(ents, key=lambda e: e.start))
    return doc


# @Language.component("merge_localities")
# def merge_localities(doc):
#     """Convert other traits to locality if surrounded by localities."""
#     ents = []
#
#     for ent in doc.ents:
#         # Merge: locality habitat locality
#         # Merge: locality habitat .
#         # Merge: locality habitat , locality
#         pass
#
#     doc.set_ents(sorted(ents, key=lambda e: e.start))
#     return doc
