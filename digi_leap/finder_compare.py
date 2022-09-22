#!/usr/bin/env python3
"""Compare various label finder algorithms.

The results of the data are stored in the  label_tests table. We want to compare
results from the same training set.
"""
import argparse
import textwrap
from pathlib import Path

from traiter import log


def main():
    # args = parse_args()
    log.started()
    # reconcile_expedition.reconcile(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Compare the various label finder results.

        Take the results from all label finder tests (label_tests.train_set) that link
        back to a label finder training set (label_train.train_set) and compare the
        results tests to the training sets for:
            1) Intersection over union of the labels.
            2) The classes of the labels.
        """

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--train-set",
        required=True,
        metavar="NAME",
        help="""Write new reconciled labels to this set.""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run. Enclose them in quotes.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
