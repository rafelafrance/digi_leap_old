import re
from calendar import IllegalMonthError
from datetime import date

from dateutil import parser
from dateutil.relativedelta import relativedelta
from spacy.util import registry
from traiter.pylib.patterns.matcher_patterns import MatcherPatterns
from traiter.pylib.pylib import actions


SEPARATOR = r"[./_'-]"
COMMA = r"[.,/_-]"
LABEL_ENDER = r"[:=]"
LABELS = """ date """.split()


# ####################################################################################
DECODER = {
    ",": {"TEXT": {"REGEX": f"^{COMMA}+$"}},
    "-": {"TEXT": {"REGEX": f"^{SEPARATOR}+$"}},
    ":": {"TEXT": {"REGEX": f"^{LABEL_ENDER}+$"}},
    "9_": {"TEXT": {"REGEX": r"^\d\d?$"}},
    "99": {"TEXT": {"REGEX": r"^\d\d$"}},
    "label": {"LOWER": {"IN": LABELS}},
    "month": {"ENT_TYPE": "month"},
    "9999": {"TEXT": {"REGEX": r"^[12]\d{3}$"}},
}


# ####################################################################################
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


@registry.misc(LABEL_DATE.on_match)
def on_label_date_match(ent):
    flags = re.IGNORECASE | re.VERBOSE
    text = ent.text

    if re.match(r"\d\d? \s \d\d? \s \d\d?", text, flags=flags):
        raise actions.RejectMatch()

    text = re.sub(
        rf" ({'|'.join(LABELS)}) \s* {LABEL_ENDER}* \s* ",
        "",
        text,
        flags=flags,
    )
    text = re.sub(f"{COMMA}+", " ", text, flags=flags)
    try:
        date_ = parser.parse(text).date()
    except (parser.ParserError, IllegalMonthError) as err:
        raise actions.RejectMatch() from err

    if date_ > date.today():
        date_ -= relativedelta(years=100)
        ent._.data["century_adjust"] = True

    ent._.data["label_date"] = date_.isoformat()[:10]


# ####################################################################################
MISSING_DAY = MatcherPatterns(
    "short_date",
    on_match="digi_leap.missing_day.v1",
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


@registry.misc(MISSING_DAY.on_match)
def short_date(ent):
    flags = re.IGNORECASE | re.VERBOSE
    if re.match(r"\d\d? [\s'] \d\d?", ent.text, flags=flags):
        raise actions.RejectMatch()

    on_label_date_match(ent)
    ent._.data["label_date"] = ent._.data["label_date"][:7]
    ent._.data["missing_day"] = True
    ent._.new_label = "label_date"
