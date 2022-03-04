#!/usr/bin/env python3
"""Split labeled images into training, testing, and validation datasets."""
import argparse
import sqlite3
import textwrap
from pathlib import Path

from pylib import db


def main():
    """Infer traits."""
    args = parse_args()
    assign_sheets(args)


def assign_sheets(args):
    """Assign herbarium sheets to splits."""
    run_id = db.insert_run(args)

    select = """
       select sheet_id from sheets where split is null or split = '' order by random()
    """
    rows = db.rows_as_dicts(args.database, select)

    count = len(rows)
    val_split = round(count * (args.test_split + args.val_split))
    test_split = round(count * args.test_split)

    update = """update sheets set split = ? where sheet_id = ?"""
    with sqlite3.connect(args.database) as cxn:
        for i, row in enumerate(rows):
            if i <= test_split:
                split = "test"
            elif i <= val_split:
                split = "val"
            else:
                split = "train"
            cxn.execute(update, (split, row["sheet_id"]))

    db.update_run_finished(args.database, run_id)


def parse_args():
    """Process command-line arguments."""
    description = """Split herbarium sheets into training, testing, and validation
        datasets."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        "--db",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Path to the SQLite3 database (angiosperm data).""",
    )

    arg_parser.add_argument(
        "--train-split",
        type=float,
        metavar="FRACTION",
        default=0.6,
        help="""What fraction of records to use for training the model.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--val-split",
        type=float,
        metavar="FRACTION",
        default=0.2,
        help="""What fraction of records to use for the validation. I.e. evaluating
            training progress at the end of each epoch. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--test-split",
        type=float,
        metavar="FRACTION",
        default=0.2,
        help="""What fraction of records to use for the testing. I.e. the holdout
            data used to evaluate the model after training. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--notes",
        metavar="TEXT",
        help="""Notes about this run.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
