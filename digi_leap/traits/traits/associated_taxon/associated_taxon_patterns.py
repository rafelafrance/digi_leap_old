from traiter.traits.pattern_compiler import Compiler


def associated_taxon_patterns():
    decoder = {
        "assoc": {"ENT_TYPE": "assoc"},
        "label": {"ENT_TYPE": "assoc_label"},
    }
    return [
        Compiler(
            label="assoc_taxon",
            decoder=decoder,
            patterns=[
                "assoc label",
            ],
        ),
    ]
