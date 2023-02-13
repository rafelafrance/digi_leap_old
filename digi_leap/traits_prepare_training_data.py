#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import validate_args
from pylib.traits import prepare_data
from traiter.pylib import log


def main():
    log.started()
    args = parse_args()
    prepare_data.prepare(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Save training data for training an NER model."""

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
        help="""The name of the trait set.""",
    )

    arg_parser.add_argument(
        "--out-file",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Output the spaCy NER training data to this file.""",
    )

    args = arg_parser.parse_args()
    validate_args.validate_trait_set(args.database, args.trait_set)
    return args


if __name__ == "__main__":
    main()
