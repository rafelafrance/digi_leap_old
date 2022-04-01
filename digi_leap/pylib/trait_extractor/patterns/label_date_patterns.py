"""Parse date notations."""
from calendar import IllegalMonthError
from datetime import date

import regex as re
from dateutil import parser
from dateutil.relativedelta import relativedelta
from spacy import registry
from traiter import actions
from traiter.patterns.matcher_patterns import MatcherPatterns


class LabelDate:
    """Constants for parsing label dates."""

    separator = r"[/_-]"
    comma = r"[,/_-]"
    label_ender = r"[:=]"
    labels = """ date """.split()


# ####################################################################################
def label_date_decoder():
    """Get the label date decoder."""
    return {
        ",": {"TEXT": {"REGEX": f"^{LabelDate.comma}+$"}},
        "-": {"TEXT": {"REGEX": f"^{LabelDate.separator}+$"}},
        ":": {"TEXT": {"REGEX": f"^{LabelDate.label_ender}+$"}},
        "9_": {"TEXT": {"REGEX": r"^\d\d?$"}},
        "99": {"TEXT": {"REGEX": r"^\d\d$"}},
        "label": {"LOWER": {"IN": LabelDate.labels}},
        "month": {"ENT_TYPE": "month"},
        "9999": {"TEXT": {"REGEX": r"^[12]\d{3}$"}},
    }


# ####################################################################################
ON_LABEL_DATE_MATCH = "digi_leap.label_date.v1"


def build_label_date_patterns():
    """Build common label date patterns."""
    return MatcherPatterns(
        "label_date",
        on_match=ON_LABEL_DATE_MATCH,
        decoder=label_date_decoder(),
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


@registry.misc(ON_LABEL_DATE_MATCH)
def on_label_date_match(ent):
    """Parse date notations."""
    flags = re.IGNORECASE | re.VERBOSE
    text = ent.text
    text = re.sub(
        fr" ({'|'.join(LabelDate.labels)}) \s* {LabelDate.label_ender}* \s* ",
        "",
        text,
        flags=flags,
    )
    text = re.sub(f"{LabelDate.comma}+", " ", text, flags=flags)
    try:
        date_ = parser.parse(text).date()
    except (parser.ParserError, IllegalMonthError):
        raise actions.RejectMatch

    if date_ > date.today():
        date_ -= relativedelta(years=100)
        ent._.data["century_adjust"] = True

    ent._.data["label_date"] = date_.isoformat()[:10]


# ####################################################################################
ON_MISSING_DAY_MATCH = "digi_leap.missing_day.v1"


def build_missing_day_patterns():
    """Build label date patterns that are missing a day."""
    return MatcherPatterns(
        "short_date",
        on_match=ON_MISSING_DAY_MATCH,
        decoder=label_date_decoder(),
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


@registry.misc(ON_MISSING_DAY_MATCH)
def short_date(ent):
    """Normalize a month year as all digits notation."""
    on_label_date_match(ent)
    ent._.data["label_date"] = ent._.data["label_date"][:7]
    ent._.data["missing_day"] = True
    ent._.new_label = "label_date"
