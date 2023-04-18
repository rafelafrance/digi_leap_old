from pathlib import Path

from spacy import Language

LABEL_ASSOC_TAXON = "label_assoc_taxon"

ASSOC_CSV = Path(__file__).parent / "associated_taxon_terms.csv"


PRIMARY_RANKS = set(""" species subspecies variety subvariety form subform """.split())


@Language.component(LABEL_ASSOC_TAXON)
def label_assoc_taxon(doc):
    """Mark taxa in the document as either primary or associated."""
    primary_ok = True

    for ent in doc.ents:

        if ent.label_ == "assoc_taxon":
            primary_ok = False

        elif ent.label_ == "taxon":

            if primary_ok and ent._.data["rank"] in PRIMARY_RANKS:
                ent._.data["primary"] = "primary"
                primary_ok = False

            else:
                ent._.data["primary"] = "associated"

    return doc
