from spacy.util import registry
from traiter.pylib.pattern_compilers.matcher_compiler import MatcherCompiler

DECODER = {
    "assoc": {"LOWER": {"IN": ["associated", "assoc"]}},
    "label": {"LOWER": {"IN": ["species", "taxa", "taxon"]}},
}

# ####################################################################################
ASSOC_TAXA = MatcherCompiler(
    "associated_taxa",
    decoder=DECODER,
    patterns=[
        "assoc label",
    ],
)
