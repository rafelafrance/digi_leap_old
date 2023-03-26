from spacy.language import Language
from spacy.tokens import Doc
from traiter.pylib.matcher_patterns import MatcherPatterns

# #################################################################################
ASSOC_TAXA = MatcherPatterns(
    "associated_taxa",
    on_match=None,
    decoder={
        "assoc": {"LOWER": {"IN": ["associated", "assoc"]}},
        "label": {"LOWER": {"IN": ["species", "taxa", "taxon"]}},
    },
    patterns=[
        "assoc label",
    ],
    output=None,
)

# #################################################################################
PRIMARY_TAXON = "digi_leap_primary_taxon_v1"

PRIMARY_RANKS = set(""" species subspecies variety subvariety form subform """.split())


@Language.factory(PRIMARY_TAXON)
class PrimaryTaxon:
    """Mark a taxon as primary or associated."""

    def __init__(self, nlp: Language, name: str):
        self.nlp = nlp
        self.name = name

    def __call__(self, doc: Doc) -> Doc:
        primary_ok = True
        for ent in doc.ents:
            if ent.label_ == "taxon":
                if primary_ok and ent._.data["rank"] in PRIMARY_RANKS:
                    ent._.data["primary"] = "primary"
                    primary_ok = False
                else:
                    ent._.data["primary"] = "associated"
            elif ent.label_ == "associated_taxa":
                primary_ok = False

        return doc
