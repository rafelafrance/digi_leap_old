#!/usr/bin/env python
"""
Generate label text from the saved label data.

Images can be generated (both clean and dirty) on the fly but we need to
persist the text data so that it can be used in several steps further down
the pipeline. This module creates persistent data for the label text from the
iDigBio database.

Each row in the label text can be used to generate several types of labels as
well as modifying the text itself. The text will be saved in parts so that
image augmentation can be done on each section of text separately.

Note that we are generating fake labels not necessarily realistic labels.

Some text augmentation:
- Sometimes we will use field labels and other times not
- Add titles and headers
- Fields can be moved around on the label
- Omit and add data to the labels
- Augment taxon names with data from ITIS
- Generate names dates and numbers
- Replace some words with abbreviations
- Add extra spaces
- Join fields to make longer text fields

** Image augmentation happens elsewhere.

Some fields we needed:
- Field type (typed or cursive or a barcode)
- The field text itself
- Row/vertical order
- Column/horizontal order
"""

import re
import sqlite3
import string
from random import choices, seed
from textwrap import wrap

import pandas as pd

from digi_leap.pylib.const import LABEL_DB
from digi_leap.pylib.util import ended, sample_defaults, started

TYPES = 'typewritten handwritten both barcode qrcode'.split()
REMOVE_PUNCT = str.maketrans('', '', string.punctuation)

REJECTS = sample_defaults('reject_value', k=100_000)
NAMES = sample_defaults('name', k=100_000)


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


def main_label(label_id: int, row) -> list[dict]:
    """Generate a plausible main label."""
    parts = clean_line('Plants of', row['state_province'])
    parts += clean_line(row['scientific_name'], row['scientific_name_authorship'])
    parts += split_line(label='Notes', text=row['field_notes'])
    parts += split_line(label='Remarks', text=row['event_remarks'])
    parts += split_line(label='Locality', text=row['locality'])
    parts += split_line(label='Location', text=row['location_remarks'])
    parts += split_line(label='Occurrence', text=row['occurrence_remarks'])
    parts += split_line(label='Preparations', text=row['preparations'])
    parts += split_line(label='Life Stage', text=row['life_stage'])
    parts += split_line(label='Sex', text=row['sex'])
    parts += split_line(label='Condition', text=row['reproductive_condition'])
    parts += split_line(label='Coordinates', text=row['verbatim_coordinates'])

    lat = format_lat_long(row['verbatim_latitude'])
    long = format_lat_long(row['verbatim_longitude'])
    parts += clean_line(lat, long)

    return fill_in_label(label_id, parts)


def get_name(row, preferred=''):
    """Get a name to use for the field."""
    name = row[preferred]
    return name if name else choices(NAMES)


def det_label(label_id, row):
    """Generate a determination label."""
    parts = clean_line(row['scientific_name'], row['scientific_name_authorship'])
    parts += clean_line('Det. by', get_name(row, 'identified_by'))
    parts += clean_line(row['owner_'])
    return fill_in_label(label_id, parts)


# def gibberish_label(label_id, row):
#     """Generate a determination label."""
#     parts = []
#     return parts


# def barcode_label(label_id, row):
#     """Generate a determination label."""
#     parts = []
#     return parts


# def qrcode_label(label_id, row):
#     """Generate a determination label."""
#     parts = []
#     return parts


def get_label_data(label_db):
    """Get the data from the newly created label_data table."""
    with sqlite3.connect(label_db) as cxn:
        df = pd.read_sql('select * from data', cxn)
    return df


def insert_data(df, label_db):
    """Write the data to the smaller database."""
    with sqlite3.connect(label_db) as cxn:
        df.to_sql('data', cxn, if_exists='replace', index=False)


def create_label_table(label_db):
    """Build the table before we write to it so we can do early queries."""
    sql = """
        create table if not exists labels (
            label_id   INTEGER NOT NULL,
            field_type TEXT NOT NULL,
            row        INTEGER NOT NULL,
            col        INTEGER NOT NULL,
            field      TEXT
        );
        CREATE INDEX IF NOT EXISTS labels_label_id ON labels (label_id);
        CREATE INDEX IF NOT EXISTS labels_row_col ON labels (row, col);
    """
    with sqlite3.connect(label_db) as cxn:
        cxn.executescript(sql)


def max_label_id(label_db):
    """Get the max label ID so that we can add labels."""
    with sqlite3.connect(label_db) as cxn:
        cursor = cxn.execute('select coalesce(max(label_id), 0) from labels')
        max_id = cursor.fetchone()[0]
    return max_id


def generate_labels(label_db):
    """Create the label data table with augmented text data."""
    create_label_table(label_db)

    df = get_label_data(label_db)
    labels = []

    label_id = max_label_id(label_db)

    # for _ in range(3):
    for _, row in df.iterrows():
        label_id += 1
        action = choices([main_label, main_label], cum_weights=[0.5, 0.1])[0]
        recs = action(label_id, row)
        labels += recs
        if label_id >= 10:
            break

    # insert_data(df, label_db)


if __name__ == '__main__':
    started()

    seed(123)
    generate_labels(LABEL_DB)

    ended()
