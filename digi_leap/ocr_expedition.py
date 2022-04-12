#!/usr/bin/env python3
"""Create an expedition for checking the results of the OCR label builder."""
import argparse
import sys
import textwrap
from pathlib import Path

from pylib import db
from pylib.label_builder.expedition import build_expedition


def main():
    args = parse_args()
    build_expedition.build(args)


def parse_args() -> argparse.Namespace:
    description = """OCR images of labels."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to the digi-leap database.""",
    )

    arg_parser.add_argument(
        "--cons-set",
        required=True,
        metavar="NAME",
        help="""Sample this consensus set.""",
    )

    arg_parser.add_argument(
        "--expedition-dir",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Place expedition images in this directory.""",
    )

    arg_parser.add_argument(
        "--min-words",
        default=10,
        type=int,
        metavar="COUNT",
        help="""A label must have this many words to make it into the expedition.""",
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
    validate_cons_set(args.database, args.cons_set)
    return args


def validate_cons_set(database, cons_set):
    all_cons_set = [s["cons_set"] for s in db.get_cons_sets(database)]
    if cons_set in all_cons_set:
        return
    print(f"{cons_set} is not a valid consensus set.")
    print("Valid consensus sets are:")
    print(", ".join(all_cons_set))
    sys.exit()


if __name__ == "__main__":
    main()
