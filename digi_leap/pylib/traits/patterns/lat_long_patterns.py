from spacy.util import registry
from traiter.pylib.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns


LAT_LONG = MatcherPatterns(
    "lat_long",
    on_match="digi_leap.lat_long.v1",
    decoder=common_patterns.PATTERNS
    | {
        "180": {"TEXT": {"REGEX": r"""^[-]?(1[0-8]\d|\d{1,2})$"""}},
        "60": {"TEXT": {"REGEX": r"""^([1-5]\d|\d)$"""}},
        "deg": {"TEXT": {"REGEX": r"""^[°]$"""}},
        "min": {"TEXT": {"REGEX": r"""^['`‘´’]$"""}},
        "sec": {"TEXT": {"REGEX": r"""^["”“]$"""}},
        "dir": {"TEXT": {"REGEX": r"""^[NESWnesw]\.?$"""}},
    },
    patterns=[
        "180 deg 60 min 60 sec dir ,? 180 deg 60 min 60 sec dir",
        "180 deg 60 min        dir ,? 180 deg 60 min        dir",
    ],
)


@registry.misc(LAT_LONG.on_match)
def on_lat_long_match(_):
    pass
