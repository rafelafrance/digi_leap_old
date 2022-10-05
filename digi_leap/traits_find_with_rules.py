#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib.traits import ner
from traiter import log

from digi_leap.pylib import validate_args


def main():
    log.started()
    args = parse_args()
    ner.ner(args)
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
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--trait-set",
        required=True,
        metavar="NAME",
        help="""Name the trait set.""",
    )

    arg_parser.add_argument(
        "--ocr-set",
        required=True,
        metavar="NAME",
        help="""Extract traits from this OCR set.""",
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
        help="""Notes about this run. Enclose them in quotes.""",
    )

    args = arg_parser.parse_args()
    validate_args.validate_ocr_set(args.database, args.ocr_set)
    return args


if __name__ == "__main__":
    main()
