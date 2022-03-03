#!/usr/bin/env python3
"""OCR a set of labels."""
import argparse
import textwrap
from datetime import datetime
from pathlib import Path

from pylib import ocr_labels


def main():
    """Run it."""
    args = parse_args()
    ocr_labels.ocr_labels(args)


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """OCR images of labels."""

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
        "--ocr-set",
        default=default,
        help="""Name the label finder run. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--pipelines",
        choices=["deskew", "binarize", "denoise"],
        default=["deskew", "binarize"],
        type=str,
        nargs="*",
        help="""Pipelines of image transformations that help with the OCR process.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--ocr-engines",
        choices=["tesseract", "easy"],
        default=["tesseract", "easy"],
        type=str,
        nargs="*",
        help="""Which OCR engines to use. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--classes",
        choices=["Barcode", "Handwritten", "Typewritten", "Both"],
        default=["Typewritten"],
        type=str,
        nargs="*",
        help="""Keep labels if they fall into any of these categories.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--ruler-ratio",
        type=float,
        help="""Consider a label to be a ruler if the height:width
            (or width:height) ratio is above this.""",
    )

    arg_parser.add_argument(
        "--keep-n-largest",
        type=int,
        help="""Keep the N largest labels for each sheet.""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    arg_parser.add_argument(
        "--notes",
        metavar="TEXT",
        help="""Notes about this run.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
