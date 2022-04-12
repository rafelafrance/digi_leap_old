"""Find taxon notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns
from . import term_utils

LEVEL_LOWER = """ species subspecies variety subvariety form subform """.split()

TAXON = MatcherPatterns(
    "taxon",
    on_match="digi_leap.taxon.v1",
    decoder=common_patterns.PATTERNS
    | {
        "auth": {"POS": "PROPN"},
        "maybe": {"POS": "NOUN"},
        "taxon": {"ENT_TYPE": "plant_taxon"},
        "level": {"ENT_TYPE": "level"},
        "word": {"LOWER": {"REGEX": r"^[a-z-]+$"}},
    },
    patterns=[
        "taxon+ (? auth* )?",
        "taxon+ (? auth+ maybe auth+ )?",
        "taxon+ (? auth* )?             level .? word",
        "taxon+ (? auth+ maybe auth+ )? level .? word",
    ],
)


@registry.misc(TAXON.on_match)
def on_taxon_match(ent):
    """Enrich a taxon match."""
    auth = []
    used_levels = []
    is_level = ""

    for token in ent:
        if token._.cached_label == "level":
            is_level = term_utils.VOCAB_REPLACE.get(token.lower_, token.lower_)
        elif is_level:
            ent._.data[is_level] = token.lower_
            is_level = ""

        elif token._.cached_label == "plant_taxon":
            levels = term_utils.LEVEL.get(token.lower_, ["unknown"])

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
