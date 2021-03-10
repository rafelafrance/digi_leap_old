#!/usr/bin/env python
"""Generate label text from the saved label data."""

import argparse
import sqlite3
import textwrap
from random import choices, seed

import pandas as pd

from digi_leap.pylib.label_util import (
    clean_line, fill_in_label, format_lat_long, get_value, split_line)
from digi_leap.pylib.util import choose_defaults, ended, log, started

TYPES = 'typewritten handwritten both barcode qrcode'.split()

K = 100_000
NAMES = choose_defaults('names', k=K)
DATES = choose_defaults('dates', k=K)
RIGHTS_HOLDERS = choose_defaults('rights_holders', k=K)


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


def det_label(label_id, row):
    """Generate a determination label."""
    parts = clean_line(row['scientific_name'], row['scientific_name_authorship'])
    parts += clean_line('Det. by', get_value(row, 'identified_by', NAMES))
    parts += clean_line(get_value(row, 'date_identified', DATES))
    parts += clean_line(get_value(row, 'rights_holder', RIGHTS_HOLDERS))
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


def get_label_data(database):
    """Get the data from the newly created label_data table."""
    log('Getting label data')
    with sqlite3.connect(database) as cxn:
        df = pd.read_sql('select * from data', cxn)
    return df


def insert_data(df, database):
    """Write the data to the smaller database."""
    with sqlite3.connect(database) as cxn:
        df.to_sql('data', cxn, if_exists='replace', index=False)


def create_label_table(database):
    """Build the table before we write to it so we can do early queries."""
    log('Creating label table')
    sql = """
        create table if not exists labels (
            label_id   INTEGER NOT NULL,
            field_type TEXT NOT NULL,
            row        INTEGER NOT NULL,
            col        INTEGER NOT NULL,
            data       TEXT
        );
        CREATE INDEX IF NOT EXISTS labels_label_id ON labels (label_id);
        CREATE INDEX IF NOT EXISTS labels_row_col ON labels (row, col);
    """
    with sqlite3.connect(database) as cxn:
        cxn.executescript(sql)


def max_label_id(database):
    """Get the max label ID so that we can add labels."""
    with sqlite3.connect(database) as cxn:
        cursor = cxn.execute('select coalesce(max(label_id), 0) from labels')
        max_id = cursor.fetchone()[0]
    return max_id


def generate_labels(args):
    """Create the label data table with augmented text data."""
    seed(args.seed)

    create_label_table(args.database)

    df = get_label_data(args.database)
    labels = []

    label_id = max_label_id(args.database)

    log('Building labels')
    # for _ in range(3):
    for _, row in df.iterrows():
        label_id += 1
        action = choices([main_label, det_label], weights=[0, 10])[0]
        recs = action(label_id, row)
        labels += recs

        from pprint import pp
        pp(recs)
        print()

        if label_id >= 10:
            break

    # insert_data(df, label_db)


def parse_args():
    """Process command-line arguments."""
    description = """
    Generate label text from the saved label data.

    Images can be generated (both clean and dirty) on the fly but we need to
    persist the text data so that it can be used in several steps further down
    the pipeline. This module creates persistent data for the label text from the
    iDigBio database.
    
    Each row in the label text can be used to generate several types of labels as
    well as modifying the text itself. The text will be saved in parts so that
    image augmentation can be done on each section of text separately.
    
    Note that we are generating fake labels not necessarily realistic labels.
    
    ** Image augmentation happens elsewhere.
    """
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--database', '-d', required=True,
        help="""Path to the database.""")

    arg_parser.add_argument(
        '--clear-labels', '-c', action='store_true',
        help="""Drop the labels table before starting.""")

    arg_parser.add_argument(
        '--seed', '-s', type=int, default=123,
        help="""A random seed.""")

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    generate_labels(ARGS)

    ended()
