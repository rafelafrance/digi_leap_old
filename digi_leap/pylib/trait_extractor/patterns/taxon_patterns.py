"""Find taxon notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns
from .terms import VocabTerms


ON_TAXON_MATCH = "digi_leap.taxon.v1"
LEVEL_LOWER = """ species subspecies variety subvariety form subform """.split()

SUBSPECIES = "ssp subspecies subsp".split()
VARIETY = "var variety".split()


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
            "ssp": {"LOWER": {"IN": SUBSPECIES}},
            "var": {"LOWER": {"IN": VARIETY}},
            "word": {"LOWER": {"REGEX": r"^[a-z-]+$"}},
        },
        patterns=[
            "taxon+ (? auth* )?",
            "taxon+ (? auth+ maybe auth+ )?",
            "taxon+ (? auth* )?             ssp .? word",
            "taxon+ (? auth+ maybe auth+ )? ssp .? word",
            "taxon+ (? auth* )?             var .? word",
            "taxon+ (? auth+ maybe auth+ )? var .? word",
        ],
    )


@registry.misc(ON_TAXON_MATCH)
def on_taxon_match(ent):
    """Enrich a taxon match."""
    auth = []
    used_levels = []
    is_spp, is_var = False, False

    for token in ent:
        if token.lower_ in SUBSPECIES:
            is_spp = True
        elif token.lower_ in VARIETY:
            is_var = True
        elif is_spp:
            ent._.data["subspecies"] = token.lower_
            is_spp = False
        elif is_var:
            ent._.data["variety"] = token.lower_
            is_var = False

        elif token._.cached_label == "plant_taxon":
            levels = VocabTerms.level.get(token.lower_, ["unknown"])

            # Find the highest unused taxon level
            for level in levels:
                if level not in used_levels:
                    used_levels.append(level)
                    if level in LEVEL_LOWER:
                        ent._.data[level] = token.lower_
                    else:
                        ent._.data[level] = token.lower_.title()
                    break
            else:
                ent._.data["unknown_taxon"] = token.text

        elif token.pos_ in ["PROPN", "NOUN"]:
            auth.append(token.text)

    if auth:
        ent._.data["authority"] = " ".join(auth)

    if ent._.data.get("plant_taxon"):
        del ent._.data["plant_taxon"]
