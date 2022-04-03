"""Find taxon notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns
from .terms import VocabTerms


ON_TAXON_MATCH = "digi_leap.taxon.v1"
LEVEL_LOWER = """ species subspecies variety subvariety form subform """.split()

SSP = "ssp subspecies subsp".split()
VAR = "var variety".split()


def build_taxon_patterns():
    """Build taxon patterns."""
    return MatcherPatterns(
        "taxon",
        on_match=ON_TAXON_MATCH,
        decoder=common_patterns.get_common_patterns()
        | {
            "auth": {"POS": "PROPN"},
            "maybe": {"POS": "NOUN"},
            "taxon": {"ENT_TYPE": "plant_taxon"},
            "ssp": {"LOWER": {"IN": SSP}},
            "var": {"LOWER": {"IN": VAR}},
            "word": {"LOWER": {"REGEX": r"^[a-z-]+$"}},
        },
        patterns=[
            "taxon+ (? auth* )?",
            "taxon+ (? auth+ maybe auth+ )?",
            "taxon+ (? auth* )?             ssp .? word",
            "taxon+ (? auth+ maybe auth+ )? ssp .? word",
        ],
    )


@registry.misc(ON_TAXON_MATCH)
def on_taxon_match(ent):
    """Enrich a taxon match."""
    auth = []
    used_levels = []
    next_is_spp, next_is_var = False, False
    for token in ent:
        if token.lower_ in SSP:
            ent._.data["subspecies"] = token.lower_
            next_is_spp = True
        elif token.lower_ in VAR:
            ent._.data["variety"] = token.lower_
            next_is_var = True
        elif next_is_spp:
            next_is_spp = False
        elif next_is_var:
            next_is_var = False
        elif token._.cached_label == "plant_taxon":
            levels = VocabTerms.level.get(token.lower_, ["unknown"])

            # Find the highest unused level
            for level in levels:
                if level not in used_levels:
                    used_levels.append(level)
                    if level in LEVEL_LOWER:
                        ent._.data[level] = token.lower_
                    else:
                        ent._.data[level] = token.lower_.title()
                    break

        elif token.pos_ in ["PROPN", "NOUN"]:
            auth.append(token.text)

    # ent._.data["taxon"] = " ".join(taxon)
    if auth:
        ent._.data["authority"] = " ".join(auth)
