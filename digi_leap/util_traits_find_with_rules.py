#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import validate_args
from traiter.pylib import log

from digi_leap.traits import HtmlWriter
from digi_leap.traits import LabelReader
from digi_leap.traits import ner


def main():
    log.started()
    args = parse_args()

    ner.ner(args)

    if args.out_html:
        reader = LabelReader(args)
        writer = HtmlWriter(args.out_html)
        writer.write(reader.labels, args.trait_set)

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
        help="""A label must have at least this many words for parsing.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--out-html",
        type=Path,
        metavar="PATH",
        help="""Output the results to this HTML file.""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Sample this many labels.""",
    )

    arg_parser.add_argument(
        "--label-id",
        type=int,
        metavar="ID",
        help="""Select only this label ID. Used for testing.""",
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
