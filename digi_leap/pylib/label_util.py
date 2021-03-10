"""Functions used to generate labels."""

import re
import string
from random import choice
from textwrap import wrap

from digi_leap.pylib.const import REJECTS

REMOVE_PUNCT = str.maketrans('', '', string.punctuation)


def fill_in_label(label_id: int, parts: list[list[str]]):
    """Add label fields needed by the database."""
    recs = []
    for r, row in enumerate(parts):
        for c, field in enumerate(row):
            if field:
                recs.append({
                    'label_id': label_id,
                    'field_type': 'typewritten',
                    'row': r,
                    'col': c,
                    'field': field,
                })
    return recs


def split_line(text: str = '', label: str = '', len_: int = 40) -> list[list[str]]:
    """Split text into an array of lines."""
    lines = []

    if label:
        split = len_ - len(label)
        first, text = text[:split], text[split:].lstrip()
        if first.lower().translate(REMOVE_PUNCT) not in REJECTS:
            lines.append([label, first])

    lines += [[t] for t in wrap(text, len_)
              if t and t.lower().translate(REMOVE_PUNCT) not in REJECTS]

    return lines


def clean_line(*text: str) -> list[list[str]]:
    """Cleanup the row of strings."""
    lines = []

    # Handle the case where one field partially replicates the preceding one.
    # This happens often with scientific_name and scientific_name_authorship fields.
    for ln in text:
        if not lines or lines[-1].find(ln) < 0:
            lines.append(ln)

    return [lines]


def get_value(row, key, defaults):
    """Get a value from the record or chose a random default."""
    value = row.get(key)
    return value if value else choice(defaults)


def format_lat_long(lat_long):
    """Put degree, minute, and seconds into a lat/long."""
    frags = lat_long.split()

    # Unused is sometimes reported as "99 99 99 N ; 99 99 99 E"
    if len(frags) > 4:
        return ''

    # Add degree, minute, second symbols
    if re.match(r'\d+ \d+ \d+(?:\.\d+)? [NnSsEeWw]]', lat_long):
        deg, min_, sec, dir_ = frags
        lat_long = f'[~]?{deg}°{min_}′{sec}″{dir_}'
    elif re.match(r'\d+ \d+ [NnSsEeWw]]', lat_long):
        deg, min_, dir_ = frags
        lat_long = f'[~]?{deg}°{min_}′{dir_}'

    return lat_long
