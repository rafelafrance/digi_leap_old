from traiter.pylib.traits.pattern_compiler import Compiler

from . import associated_taxon_action as act


def associated_taxon_patterns():
    decoder = {
        "assoc": {"ENT_TYPE": "assoc"},
        "label": {"ENT_TYPE": "assoc_label"},
    }
    return [
        Compiler(
            label="assoc_taxon",
            on_match=act.ASSOC_TAXON_MATCH,
            decoder=decoder,
            patterns=[
                "assoc label",
            ],
        ),
    ]
