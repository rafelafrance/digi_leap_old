#!/usr/bin/env python3
"""OCR a set of labels."""
import argparse
import textwrap
from pathlib import Path

from .ocr import label_transformer as xform
from .ocr import ocr_labels
from .pylib import consts


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
        help="""Create this label set.""",
    )

    arg_parser.add_argument(
        "--pipelines",
        choices=list(xform.TRANSFORM_PIPELINES.keys()),
        default=list(xform.TRANSFORM_PIPELINES.keys())[:2],
        type=str,
        nargs="*",
        help="""Pipelines of image transformations that help with the OCR process.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--ocr-engines",
        choices=list(ocr_labels.ENGINE.keys()),
        default=list(ocr_labels.ENGINE.keys()),
        type=str,
        nargs="*",
        help="""Which OCR engines to use. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--classes",
        choices=consts.CLASSES[1:],
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
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
