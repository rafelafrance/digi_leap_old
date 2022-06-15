#!/usr/bin/env python3
"""Create an expedition for checking the results of the OCR label builder."""
import argparse
import textwrap
from pathlib import Path

from pylib import validate_args
from pylib.label_builder.expedition import build_expedition


def main():
    args = parse_args()
    build_expedition.build(args)


def parse_args() -> argparse.Namespace:
    description = """Build an expedition to determine the quality of the
        label builder."""

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
        "--consensus-set",
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
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run. Enclose them in quotes.""",
    )

    args = arg_parser.parse_args()
    validate_args.validate_cons_set(args.database, args.consensus_set)
    return args


if __name__ == "__main__":
    main()
