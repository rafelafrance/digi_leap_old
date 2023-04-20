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

            taxon = ent._.data["taxon"]
            rank = ent._.data["rank"]

            if primary_ok and rank in PRIMARY_RANKS and len(taxon.split()) > 1:
                primary_ok = False

            else:
                relabel_entity(ent, "associated_taxon")
                ent._.data["trait"] = "associated_taxon"
                ent._.data["associated_taxon"] = taxon
                del ent._.data["taxon"]

    return doc


def relabel_entity(ent, label):
    strings = ent.doc.vocab.strings
    if label not in strings:
        strings.add(label)
    ent.label = strings[label]
