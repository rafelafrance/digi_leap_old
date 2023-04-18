#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import validate_args
from traiter.pylib import log

from digi_leap.traits.label_reader import LabelReader
from digi_leap.traits.writers.html_writer import HtmlWriter


def main():
    log.started()
    args = parse_args()

    reader = LabelReader(args)

    if args.out_html:
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
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--trait-set",
        required=True,
        metavar="NAME",
        help="""Name of the trait set.""",
    )

    arg_parser.add_argument(
        "--out-html",
        type=Path,
        metavar="PATH",
        help="""Output the results to this HTML file.""",
    )

    args = arg_parser.parse_args()
    validate_args.validate_trait_set(args.database, args.trait_set)
    return args


if __name__ == "__main__":
    main()
