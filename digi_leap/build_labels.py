#!/usr/bin/env python3
"""Find "best" labels from ensembles of OCR results of each label."""
import argparse
import textwrap
from datetime import datetime
from pathlib import Path

from .pylib import build_labels


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """
        Build a single "best" label from an ensemble of OCR outputs for
        every selected label. An ensemble is a set of OCR outputs of
        the same label using various image processing pipelines and OCR
        engines. They are grouped by OCR "runs"."""

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

    default = datetime.now().isoformat(sep="_", timespec="seconds")
    arg_parser.add_argument(
        "--cons-set",
        default=default,
        help="""Name the consensus construction run. (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--ocr-runs",
        type=str,
        nargs="*",
        help="""Which OCR runs contain the label ensembles.""",
    )

    arg_parser.add_argument(
        "--classes",
        choices=["Barcode", "Handwritten", "Typewritten", "Both"],
        type=str,
        nargs="*",
        default=["Typewritten"],
        help="""Keep labels if they fall into any of these categories.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    args = arg_parser.parse_args()
    return args


def main():
    """Run it."""
    args = parse_args()
    build_labels.build_labels(args)


if __name__ == "__main__":
    main()
