#!/usr/bin/env python3
"""Find "best" labels from ensembles of OCR results of each label."""
import argparse
import sys
import textwrap
from pathlib import Path

from pylib import db
from pylib import label_builder


def main():
    """Run it."""
    args = parse_args()
    label_builder.build_labels(args)


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """
        Build a single "best" label from an ensemble of OCR outputs for
        every selected label. An ensemble is a set of OCR outputs of
        the same label using various image processing pipelines and OCR
        engines. They are grouped by OCR "sets"."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Path to the digi-leap database.""",
    )

    arg_parser.add_argument(
        "--ocr-set",
        required=True,
        metavar="NAME",
        help="""Use this OCR set as input for building the labels.""",
    )

    arg_parser.add_argument(
        "--cons-set",
        required=True,
        metavar="NAME",
        help="""Name the consensus construction set.""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run.""",
    )

    args = arg_parser.parse_args()
    validate_ocr_set(args.database, args.ocr_set)
    return args


def validate_ocr_set(database, ocr_set):
    """Get the OCR runs included in this cons_set."""
    all_ocr_sets = [s["ocr_set"] for s in db.get_ocr_sets(database)]
    if ocr_set in all_ocr_sets:
        return
    print(f"{ocr_set} is not a valid OCR set.")
    print("Valid OCR sets are:")
    print(", ".join(all_ocr_sets))
    sys.exit()


if __name__ == "__main__":
    main()
