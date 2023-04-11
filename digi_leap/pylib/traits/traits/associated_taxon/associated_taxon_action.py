from pathlib import Path

from spacy import registry

ASSOC_TAXON_MATCH = "assoc_taxon_match"

ASSOC_CSV = Path(__file__).parent / "associated_taxon_terms.csv"


PRIMARY_RANKS = set(""" species subspecies variety subvariety form subform """.split())


@registry.misc(ASSOC_TAXON_MATCH)
def assoc_taxon_match(ent):
    """Mark taxa in the document as either primary or associated."""

    primary_ok = True

    for ent in ent.doc.ents:

        if ent.label_ == "taxon":

            if primary_ok and ent._.data["rank"] in PRIMARY_RANKS:
                ent._.data["primary"] = "primary"
                primary_ok = False

            else:
                ent._.data["primary"] = "associated"

        elif ent.label_ == "assoc_taxon":
            primary_ok = False
