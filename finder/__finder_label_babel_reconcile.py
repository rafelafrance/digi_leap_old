#!/usr/bin/env python3
"""Reconcile data from a "Label Babel" expedition.

We need training data for the label finder model. We use volunteers to build the
initial batch of training data. That is, we use a Zooniverse "Notes from Nature"
expedition to have volunteers (often 3 or more) draw the label bounding boxes. Every
bounding will be slightly different, so we use this script to reconcile the differences
into a single best label. There are many wrinkles to this process, some of which are:
    - Sometimes a person will draw a box around many labels.
    - Sometimes a box gets drawn around nothing.
    - Sometimes the drawn boxes are really large or small (outliers).
    - Etc.
So we cannot just take a simple average of the box coordinates.
"""
import argparse
import textwrap
from pathlib import Path

from pylib import log
from pylib.rise_of_machines import reconcile_expedition


def main():
    log.started()
    args = parse_args()
    reconcile_expedition.reconcile(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Reconcile data from a "Label Babel" expedition.

    We need training data for the label finder model and we use use volunteers to build
    the initial batch of training data. That is, we use a "Notes from Nature" Zooniverse
    expedition to have volunteers (often 3 or more) draw all label bounding boxes around
    every label. Every volunteer draws a slightly different bounding box, so we use this
    script to reconcile the differences into a single "best" label."""

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
        "--unreconciled-csv",
        required=True,
        metavar="PATH",
        help="""Get volunteer drawn labels from this CSV file.""",
    )

    arg_parser.add_argument(
        "--reconciled-set",
        required=True,
        metavar="NAME",
        help="""Write reconciled labels to this set.""",
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
