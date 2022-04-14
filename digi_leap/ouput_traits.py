#!/usr/bin/env python3
"""Output label text."""
import argparse
import sys
import textwrap
from pathlib import Path

from pylib import db
from pylib.trait_writer import html_writer
from traiter import log


def main():
    log.started()
    args = parse_args()

    if args.format == "html":
        html_writer.write(args)

    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Extract information from the labels."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the digi-leap database.""",
    )

    arg_parser.add_argument(
        "--trait-set",
        required=True,
        metavar="NAME",
        help="""The name of the trait set.""",
    )

    arg_parser.add_argument(
        "--out-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output the results to this file.""",
    )

    arg_parser.add_argument(
        "--format",
        choices=["html"],
        default="html",
        help="""Output the traits in this format.""",
    )

    args = arg_parser.parse_args()
    validate_trait_set(args.database, args.trait_set)
    return args


def validate_trait_set(database, trait_set):
    with db.connect(database) as cxn:
        rows = db.execute(cxn, "select distinct trait_set from traits")
        all_trait_sets = [r["trait_set"] for r in rows]

    if trait_set in all_trait_sets:
        return

    print(f"{trait_set} is not a valid trait set.")
    print("Valid trait sets are:")
    print(", ".join(all_trait_sets))
    sys.exit()


if __name__ == "__main__":
    main()
