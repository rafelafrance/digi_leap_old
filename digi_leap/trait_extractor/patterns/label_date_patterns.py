"""Parse date notations."""
from calendar import IllegalMonthError
from datetime import date

import regex as re
from dateutil import parser
from dateutil.relativedelta import relativedelta
from spacy import registry
from traiter import actions
from traiter.patterns.matcher_patterns import MatcherPatterns

SEP = r"[/_-]"
COMMA = r"[,/_-]"
ENDER = r"[:=]"
LABELS = """ date """.split()
FLAGS = re.IGNORECASE | re.VERBOSE

DECODER = {
    ",": {"TEXT": {"REGEX": f"^{COMMA}+$"}},
    "-": {"TEXT": {"REGEX": f"^{SEP}+$"}},
    ":": {"TEXT": {"REGEX": f"^{ENDER}+$"}},
    "9_": {"TEXT": {"REGEX": r"^\d\d?$"}},
    "99": {"TEXT": {"REGEX": r"^\d\d$"}},
    "label": {"LOWER": {"IN": LABELS}},
    "month": {"ENT_TYPE": "month"},
    "9999": {"TEXT": {"REGEX": r"^[12]\d{3}$"}},
}

LABEL_DATE = MatcherPatterns(
    "label_date",
    on_match="digi_leap.label_date.v1",
    decoder=DECODER,
    patterns=[
        "label? :? 9_    -? 9_    -? 9_",
        "label? :? 9_    -? 9_    ,? 9999",
        "label? :? 9_    -? month -? 9_",
        "label? :? 9_    -? month ,? 9999",
        "label? :? month ,? 9_    -? 9_",
        "label? :? month ,? 9_    ,? 9999",
        "label? :? 9999  -? 9_    -? 9_",
        "label? :? 9999  -? month -? 9_",
    ],
)

SHORT_DATE = MatcherPatterns(
    "short_date",
    on_match="digi_leap.short_date.v1",
    decoder=DECODER,
    patterns=[
        "label? :? 9_    -? 99",
        "label? :? 99    -? 9_",
        "label? :? 9_    ,? 9999",
        "label? :? month ,? 9999",
        "label? :? month ,? 99",
        "label? :? 9999  ,? 9_",
        "label? :? 9999  -? month",
    ],
)


@registry.misc(LABEL_DATE.on_match)
def label_date(ent):
    """Parse date notations."""
    text = ent.text
    text = re.sub(fr" ({'|'.join(LABELS)}) \s* {ENDER}* \s* ", "", text, flags=FLAGS)
    text = re.sub(f"{COMMA}+", " ", text, flags=FLAGS)
    try:
        date_ = parser.parse(text).date()
    except (parser.ParserError, IllegalMonthError):
        raise actions.RejectMatch

    if date_ > date.today():
        date_ -= relativedelta(years=100)
        ent._.data["century_adjust"] = True

    ent._.data["label_date"] = date_.isoformat()[:10]


@registry.misc(SHORT_DATE.on_match)
def short_date(ent):
    """Normalize a month year as all digits notation."""
    label_date(ent)
    ent._.data["label_date"] = ent._.data["label_date"][:7]
    ent._.data["missing_day"] = True
    ent._.new_label = "label_date"
