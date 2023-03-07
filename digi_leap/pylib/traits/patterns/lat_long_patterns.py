from spacy.util import registry
from traiter.pylib.pattern_compilers.matcher_compiler import MatcherCompiler

from . import common_patterns

SYMBOLS = r"""^[°"”“'`‘´’]$"""

LAT_LONG = MatcherCompiler(
    "lat_long",
    on_match="digi_leap_lat_long_v1",
    decoder=common_patterns.PATTERNS
    | {
        "label": {"LOWER": {"IN": ["gps"]}},
        "180": {"TEXT": {"REGEX": r"""^[-]?(1?[0-8]\d|\d{1,2})$"""}},
        "60": {"TEXT": {"REGEX": r"""^([1-5]\d|\d)$"""}},
        "deg": {"LOWER": {"REGEX": rf"""^({SYMBOLS}|degrees?|deg\.?)$"""}},
        "min": {"LOWER": {"REGEX": rf"""^({SYMBOLS}|minutes?|min\.?)$"""}},
        "sec": {"LOWER": {"REGEX": rf"""^({SYMBOLS}|seconds?|sec\.?)$"""}},
        "dir": {"LOWER": {"REGEX": r"""^[nesw]\.?$"""}},
    },
    patterns=[
        "label? 180 deg? 60 min? 60 sec? dir ,? 180 deg? 60 min? 60 sec? dir",
        "label? 180 deg? 60 min?         dir ,? 180 deg? 60 min?         dir",
    ],
)


@registry.misc(LAT_LONG.on_match)
def on_lat_long_match(ent):
    ent._.data["lat_long"] = ent.text
