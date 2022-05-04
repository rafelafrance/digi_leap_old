#!/usr/bin/env python3
"""Split labeled images into training, testing, and validation datasets."""
import argparse
import sys
import textwrap
from pathlib import Path

from pylib.db import db


def main():
    args = parse_args()
    assign_sheets(args)


def assign_sheets(args):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        select = """
            select sheet_id from sheets
             where split is null or split = '' order by random()
            """
        rows = db.execute(cxn, select)

        count = len(rows)
        val_split = round(count * (args.eval_split + args.val_split))
        eval_split = round(count * args.eval_split)

        update = """update sheets set split = ? where sheet_id = ?"""
        for i, row in enumerate(rows):
            if i <= eval_split:
                split = "test"
            elif i <= val_split:
                split = "val"
            else:
                split = "train"
            db.execute(cxn, update, (split, row["sheet_id"]))

        db.update_run_finished(cxn, run_id)


def parse_args():
    description = """Split herbarium sheets into training, testing, and validation
        datasets."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Path to a digi-leap database.""",
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
        help="""What fraction of records to use for testing. I.e. the holdout
            data used to evaluate the model after training. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run.""",
    )

    args = arg_parser.parse_args()

    if args.train_split + args.val_split + args.test_split != 1.0:
        sys.exit("""train-split + val-split + test-split must sum to 1.0""")

    return args


if __name__ == "__main__":
    main()
