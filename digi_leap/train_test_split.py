#!/usr/bin/env python
"""Split the reconciled Label Babel JSONL file into training & test JSONL files.

The training set will contain both the training and validation data. The test set is
also known as a holdout set.
"""

import argparse
import textwrap
from pathlib import Path

from sklearn.model_selection import train_test_split

import pylib.log as log


def split(args):
    """Split the dataset."""
    with open(args.reconciled_jsonl) as in_file:
        subjects = in_file.readlines()

    train_subjects, test_subjects = train_test_split(subjects, test_size=args.split)

    with open(args.train_jsonl, 'w') as out_file:
        out_file.writelines(train_subjects)

    with open(args.test_jsonl, 'w') as out_file:
        out_file.writelines(test_subjects)


def parse_args():
    """Process command-line arguments."""
    description = """Train a model to find labels on herbarium sheets."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--reconciled-jsonl",
        required=True,
        type=Path,
        help="""The JSONL file containing reconciled bounding boxes.""",
    )

    arg_parser.add_argument(
        "--train-jsonl",
        required=True,
        type=Path,
        help="""The JSONL file containing reconciled bounding boxes.""",
    )

    arg_parser.add_argument(
        "--test-jsonl",
        required=True,
        type=Path,
        help="""The JSONL file containing reconciled bounding boxes.""",
    )

    arg_parser.add_argument(
        "--split",
        type=float,
        default=0.2,
        help="""Fraction of subjects in the test dataset. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    split(ARGS)

    log.finished()
