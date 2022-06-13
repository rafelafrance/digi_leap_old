#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import validate_args
from pylib.ner.writers import html_writer
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
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--trait-set",
        required=True,
        metavar="NAME",
        help="""Name this trait set.""",
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
    validate_args.validate_trait_set(args.database, args.trait_set)
    return args


if __name__ == "__main__":
    main()
