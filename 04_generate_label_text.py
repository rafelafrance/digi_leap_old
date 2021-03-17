#!/usr/bin/env python
"""Generate label text from the saved label data."""

import argparse
import logging
import sqlite3
import textwrap
from random import choices, randint, seed

import pandas as pd
from tqdm import tqdm

from digi_leap.db import sample_values
from digi_leap.label_text import LabelText
from digi_leap.log import finished, started


def main_label(row, _):
    """Generate a plausible main label."""
    label = LabelText(row)

    label.add_title()
    label.add_sci_name()
    label.split_text(row.get('dwc:fieldNotes'))
    label.split_text(row.get('dwc:eventRemarks'))
    label.split_text(row.get('dwc:locality'))
    label.split_text(row.get('dwc:locationRemarks'))
    label.split_text(row.get('dwc:occurrenceRemarks'))
    label.split_text(row.get('dwc:preparations'))
    label.split_text(row.get('dwc:lifeStage'))
    label.split_text(row.get('dwc:sex'))
    label.split_text(row.get('dwc:reproductiveCondition'))
    label.add_lat_long()

    return label.build_records()


def det_label(row, impute):
    """Generate a plausible determination label."""
    label = LabelText(row)

    label.add_sci_name()

    label.impute_text(
        row.get('dwc:identifiedBy'),
        impute['name'],
        field_label='Det. by',
        use='name')

    label.impute_text(
        row.get('dwc:dateIdentified'),
        impute['date'],
        use='date')

    label.impute_text(
        row.get('dcterms:rightsHolder'),
        impute['rights_holder'],
        use='rights_holder')

    return label.build_records()


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
    logging.info('Getting label data')
    with sqlite3.connect(args.database) as cxn:
        last = cxn.execute(f'select count(*) from {args.input_table}').fetchone()[0]
        offset = randint(0, last - args.count - 1)
        df = pd.read_sql(f"""
            select * from {args.input_table}
            limit {args.count}
            offset {offset}""", cxn)
    return df


def insert_data(args, labels):
    """Write the data to the smaller database."""
    logging.info('Writing labels')

    if_exists = 'replace' if args.clear_labels else 'append'

    sql = f"""
        CREATE INDEX IF NOT EXISTS labels_row_col
            ON {args.output_table} (label_id, row, col);
    """

    df = pd.DataFrame(labels)

    with sqlite3.connect(args.database) as cxn:
        df.to_sql(args.output_table, cxn, if_exists=if_exists, index=False)
        cxn.executescript(sql)


def generate_labels(args):
    """Create the label data table with augmented text data."""
    if args.seed:
        seed(args.seed)

    impute = {
        'name': sample_values(args.database, 'names', k=args.count),
        'date': sample_values(args.database, 'dates', k=args.count),
        'rights_holder': sample_values(args.database, 'rights_holders', k=args.count),
    }

    df = get_label_data(args)
    labels = []

    logging.info('Building labels')
    for _, row in tqdm(df.iterrows()):
        action = choices([main_label, det_label], weights=[10, 10])[0]
        recs = action(row, impute)
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
    image augmentation can be finished on each section of text separately.

    Note that we are generating fake labels not necessarily realistic labels.

    ** Image augmentation happens elsewhere. **
    """
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--database', '-d', required=True,
        help="""Path to the database.""")

    arg_parser.add_argument(
        '--input-table', '-i', default='occurrence_raw',
        help=f"""Get data from this table. (default: %(default))""")

    arg_parser.add_argument(
        '--output-table', '-o', default='labels',
        help=f"""Write the output to this table. (default: %(default))""")

    arg_parser.add_argument(
        '--clear-labels', '-c', action='store_true',
        help="""Drop the labels table before starting.""")

    arg_parser.add_argument(
        '--count', '-C', type=int, default=100_000,
        help=f"""The number of labels to generate. (default: %(default)s)""")

    arg_parser.add_argument(
        '--seed', '-S', type=int,
        help="""Create a random seed for python. (default: %(default)s)""")

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    generate_labels(ARGS)

    finished()
