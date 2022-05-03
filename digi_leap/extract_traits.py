#!/usr/bin/env python3
"""Parse label text."""
import argparse
import sys
import textwrap
from pathlib import Path

from pylib import db
from pylib.rule_extractor import extractor
from traiter import log


def main():
    log.started()
    args = parse_args()
    extractor.extract(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Extract information from the labels."""

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
        "--trait-set",
        required=True,
        metavar="NAME",
        help="""Name the trait set.""",
    )

    arg_parser.add_argument(
        "--cons-set",
        required=True,
        metavar="NAME",
        help="""Extract traits from this consensus label set.""",
    )

    arg_parser.add_argument(
        "--word-threshold",
        metavar="INT",
        default=20,
        help="""A label must have at least this many words for parsing.""",
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
    with db.connect(database) as cxn:
        rows = db.execute(cxn, "select distinct cons_set from cons")
        all_cons_sets = [r["cons_set"] for r in rows]

    if cons_set in all_cons_sets:
        return

    print(f"{cons_set} is not a valid consensus set.")
    print("Valid consensus sets are:")
    print(", ".join(all_cons_sets))
    sys.exit()


if __name__ == "__main__":
    main()
