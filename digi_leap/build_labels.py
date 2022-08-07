#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import log
from pylib import validate_args
from pylib.label_builder import label_builder


def main():
    log.started()
    args = parse_args()
    label_builder.build_labels(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """
        Build a single "best" label from an ensemble of OCR outputs for
        every selected label. An ensemble is a set of OCR outputs of
        the same label using various image processing pipelines and OCR
        engines. They are grouped by OCR "sets"."""

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
        "--ocr-set",
        required=True,
        metavar="NAME",
        help="""Use this OCR set as input for building the labels.""",
    )

    arg_parser.add_argument(
        "--consensus-set",
        required=True,
        metavar="NAME",
        help="""Name the consensus set.""",
    )

    arg_parser.add_argument(
        "--char-set",
        default="default",
        metavar="NAME",
        help="""Use this character set substitution matrix. (default: %(default)s)""",
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
        help="""Number of labels per batch. (default: %(default)s)""",
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
