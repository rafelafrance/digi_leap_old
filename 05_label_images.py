#!/usr/bin/env python
"""Generate label images from the saved label text."""

import argparse
import sqlite3
import textwrap
from collections import defaultdict
from random import sample, seed

from digi_leap.pylib.const import SEED
from digi_leap.pylib.util import finished, started, dict_factory


def get_labels(args):
    """Sample the label data so that we can update"""
    sql = f"""
        with chosen as (
            select distinct label_id
              from {args.input_table}
          order by random()
             limit {args.count}
        )
        select * from {args.input_table}
         where label_id in (select label_id from chosen)
      order by label_id, row, col
    """
    labels = defaultdict(list)
    with sqlite3.connect(args.database) as cxn:
        cxn.row_factory = dict_factory
        for row in cxn.execute(sql).fetchall():
            labels[row.label_id].append(row)
    return labels


def ransom_note(label):
    """Generate a label."""
    print('-' * 80)
    for row in label:
        for col in row:
            print(col)
        print()


def organize_text(label):
    """Organize text into rows and columns."""
    rows = []
    cols = []
    prev = -1
    for rec in label:
        if rec.row != prev:
            prev = rec.row
            if cols:
                rows.append(cols)
                cols = []
        cols.append(rec)

    return rows


def generate_images(args):
    """Generate images."""
    seed(args.seed)

    labels = get_labels(args)
    keys = sample(list(labels.keys()), len(labels))
    for key in keys:
        label = labels[key]
        label = organize_text(label)
        ransom_note(label)


def parse_args():
    """Process command-line arguments."""
    description = """
        Generate label images from the saved label text.

        We can generate both normal and augmented images.
    """
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--database', '-d', required=True,
        help="""Path to the database.""")

    arg_parser.add_argument(
        '--input-table', '-i', default='labels',
        help=f"""Get data from this table. (default: %(default)s)""")

    arg_parser.add_argument(
        '--count', '-c', type=int, default=100_000,
        help=f"""The number of label images to generate. (default: %(default)s)""")

    arg_parser.add_argument(
        '--no-augmented-labels', action='store_true',
        help=f"""Do not generate any augmented labels.""")

    arg_parser.add_argument(
        '--save-labels', '-s',
        help="""Save labels to this directory. Use this to save label images.""")

    arg_parser.add_argument(
        '--save-augmented', '-a',
        help="""Save augmented labels to this directory. Use this to save augmented
            label images.""")

    arg_parser.add_argument(
        '--seed', '-S', type=int, default=SEED,
        help="""Create a random seed for the python. Note: SQLite3 does not
            use seeds. (default: %(default)s)""")

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    generate_images(ARGS)

    finished()
