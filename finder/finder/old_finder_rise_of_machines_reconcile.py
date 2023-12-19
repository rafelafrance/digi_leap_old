#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib.finder.rise_of_machines import reconcile_expedition
from traiter.pylib import log


def main():
    args = parse_args()
    log.started()
    reconcile_expedition.reconcile(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Reconcile data from a "Rise of the Machines" expedition.

        This expedition is a quality control check on the label finder's output. It
        presents volunteers with herbarium sheets with outlines of the labels. The
        type of labels is indicated by the color of the outline of the label. The
        volunteers judge the correctness of found labels by clicking inside of the
        label (a point) with a correct/incorrect indicator. If the label finder
        completely missed a label a volunteer draws a bounding box around the missing
        label."""

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
        help="""Get volunteer input from this CSV file.""",
    )

    arg_parser.add_argument(
        "--label-set",
        required=True,
        metavar="NAME",
        help="""Get labels from this set.""",
    )

    arg_parser.add_argument(
        "--sheet-set",
        required=True,
        metavar="NAME",
        help="""Write reconciled sheets to this set.""",
    )

    arg_parser.add_argument(
        "--train-set",
        required=True,
        metavar="NAME",
        help="""Write new reconciled labels to this set.""",
    )

    arg_parser.add_argument(
        "--label-conf",
        type=float,
        default=0.25,
        help="""Only include labels that have a confidence >= to this. Set it to 0.0 to
            get all of the labels. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--increase-by",
        type=int,
        default=1,
        metavar="N",
        help="""Increase image size by this factor. This must match the --reduce-by N
            argument when you built the expedition with rise_of_machines_build.py.
            (default: %(default)s)""",
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
