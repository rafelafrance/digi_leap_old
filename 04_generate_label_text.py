#!/usr/bin/env python
"""Generate label text from the saved label data."""

import argparse
import sqlite3
import textwrap
from random import choices

import pandas as pd

from digi_leap.pylib.label_util import (
    clean_line, fill_in_label, format_lat_long, get_value, split_line, format_sci_name)
from digi_leap.pylib.util import ended, log, sample_values, started


def main_label(label_id, row, _) -> list[dict]:
    """Generate a plausible main label."""
    parts = clean_line('Plants of', row['dwc:stateProvince'])

    parts += format_sci_name(
        row['dwc:scientificName'], row['dwc:scientificNameAuthorship'])
    parts += split_line(label='Notes', text=row['dwc:fieldNotes'])
    parts += split_line(label='Remarks', text=row['dwc:eventRemarks'])
    parts += split_line(label='Locality', text=row['dwc:locality'])
    parts += split_line(label='Location', text=row['dwc:locationRemarks'])
    parts += split_line(label='Occurrence', text=row['dwc:occurrenceRemarks'])
    parts += split_line(label='Preparations', text=row['dwc:preparations'])
    parts += split_line(label='Life Stage', text=row['dwc:lifeStage'])
    parts += split_line(label='Sex', text=row['dwc:sex'])
    parts += split_line(label='Condition', text=row['dwc:reproductiveCondition'])
    parts += split_line(label='Coordinates', text=row['dwc:verbatimCoordinates'])

    lat = format_lat_long(row['dwc:verbatimLatitude'])
    long = format_lat_long(row['dwc:verbatimLongitude'])
    parts += clean_line(lat, long)

    return fill_in_label(label_id, parts)


def det_label(label_id, row, impute: dict[str, list[str]]):
    """Generate a determination label."""
    parts = clean_line(row['dwc:scientificName'], row['dwc:scientificNameAuthorship'])
    parts += clean_line('Det. by', get_value(row, 'dwc:identifiedBy', impute['name']))
    parts += clean_line(get_value(row, 'dwc:dateIdentified', impute['date']))
    parts += clean_line(get_value(row, 'dcterms:rightsHolder', impute['rights_holder']))
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


def get_label_data(args):
    """Get the data from the newly created label_data table."""
    log('Getting label data')
    with sqlite3.connect(args.database) as cxn:
        df = pd.read_sql(f"""
            select * from {args.input_table}
            order by random()
            limit {args.limit}""", cxn)
    return df


def insert_data(args, labels):
    """Write the data to the smaller database."""
    log('Writing labels')
    sql = f"""
        CREATE INDEX IF NOT EXISTS labels_row_col
            ON {args.output_table} (label_id, row, col);
    """
    from pprint import pp
    pp(labels)
    df = pd.DataFrame(labels)
    with sqlite3.connect(args.database) as cxn:
        df.to_sql(args.output_table, cxn, if_exists='append', index=False)
        cxn.executescript(sql)


def max_label_id(args):
    """Get the max label ID so that we can add labels."""
    if args.clear_labels:
        return 0

    with sqlite3.connect(args.database) as cxn:
        try:
            cursor = cxn.execute(f"""
                select coalesce(max(label_id), 0) from {args.output_table}""")
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0


def generate_labels(args):
    """Create the label data table with augmented text data."""
    k = 100_000
    impute = {
        'name': sample_values(args.database, 'names', k=k),
        'date': sample_values(args.database, 'dates', k=k),
        'rights_holder': sample_values(args.database, 'rights_holders', k=k),
    }

    df = get_label_data(args)
    labels = []

    label_id = max_label_id(args)

    log('Building labels')
    for _, row in df.iterrows():
        label_id += 1
        action = choices([main_label, det_label], weights=[10, 10])[0]
        recs = action(label_id, row, impute)
        labels += recs

    insert_data(args, labels)


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

    ** Image augmentation happens elsewhere. **
    """
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--database', '-d', required=True,
        help="""Path to the database.""")

    default = 'occurrence_raw'
    arg_parser.add_argument(
        '--input-table', '-i', default=default,
        help=f"""Get data from this table. The default is {default}.""")

    default = 'labels'
    arg_parser.add_argument(
        '--output-table', '-o', default=default,
        help=f"""Write the output to this table. The default is {default}.""")

    arg_parser.add_argument(
        '--clear-labels', '-c', action='store_true',
        help="""Drop the labels table before starting.""")

    default = 100_000
    arg_parser.add_argument(
        '--limit', '-l', type=int, default=default,
        help=f"""Limit the number of generated labels to make.
            The default is {default}.""")

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    generate_labels(ARGS)

    ended()
