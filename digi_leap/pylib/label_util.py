"""Functions used to generate labels."""

import re
import string
from random import choice
from textwrap import wrap

from digi_leap.pylib.const import DISALLOWED
from digi_leap.pylib.util import DotDict

REMOVE_PUNCT = str.maketrans('', '', string.punctuation)


def fill_in_label(label_id: int, parts: list[list[DotDict]]):
    """Add label fields needed by the database."""
    recs = []
    for r, row in enumerate(parts):
        for c, field in enumerate(row):
            if field:
                recs.append(DotDict({
                    'label_id': label_id,
                    'font': 'typewritten',
                    'use': field.use,
                    'row': r,
                    'col': c,
                    'text': field.text,
                }))
    return recs


def split_line(
        text: str = '', label: str = '', len_: int = 40, use: str = 'text'
) -> list[list[DotDict]]:
    """Split text into an array of lines."""
    lines = []

    if label:
        split = len_ - len(label)
        first, text = text[:split], text[split:].lstrip()
        if is_valid_value(first):
            lines.append([
                DotDict({'use': 'label', 'text': label}),
                DotDict({'use': use, 'text': first}),
            ])

    lines += [[DotDict({'use': use, 'text': t})] for t in wrap(text, len_)
              if is_valid_value(t)]

    return lines


def is_valid_value(value):
    """Check if the given value is empty or is disallowed."""
    return value and value.lower().translate(REMOVE_PUNCT) not in DISALLOWED


def clean_line(*text: str, use: str = 'text') -> list[list[DotDict]]:
    """Cleanup the row of strings."""
    line = [{'use': use, 'text': c} for c in text if c]
    return [[DotDict(c) for c in line]]


def format_sci_name(*text: str, use: str = 'sci_name') -> list[list[DotDict]]:
    """Build a scientific name and authority row."""
    lines = []

    # Handle the case where one field partially replicates the preceding one.
    for ln in text:
        if not lines or lines[-1].text.find(ln) < 0:
            lines.append(DotDict({'use': use, 'text': ln}))

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
