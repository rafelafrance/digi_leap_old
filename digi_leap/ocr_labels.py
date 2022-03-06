#!/usr/bin/env python3
"""OCR a set of labels."""
import argparse
import textwrap
from pathlib import Path

from pylib.ocr import ocr_labels
from pylib.ocr import ocr_labels_muliprocessing


def main():
    """Run it."""
    args = parse_args()

    if args.workers > 1:
        ocr_labels_muliprocessing.ocr_labels(args)
    else:
        ocr_labels.ocr_labels(args)


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """OCR images of labels."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to the digi-leap database.""",
    )

    arg_parser.add_argument(
        "--ocr-set",
        required=True,
        metavar="NAME",
        help="""Name this OCR set.""",
    )

    arg_parser.add_argument(
        "--label-set",
        required=True,
        metavar="NAME",
        help="""OCR this label set.""",
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
        "--label-conf",
        type=float,
        default=0.25,
        help="""Only OCR labels that have a confidence >= to this. Set it to 0.0 to
            get all of the labels. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--workers",
        type=int,
        metavar="INT",
        default=1,
        help="""Number of workers for processing sheets. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--batch-size",
        type=int,
        metavar="INT",
        default=10,
        help="""Number of sheets per batch. (default: %(default)s)""",
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
