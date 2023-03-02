#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib.ocr.is_correction_needed import build_expedition
from traiter.pylib import log


def main():
    log.started()
    args = parse_args()
    build_expedition.build_3_files(args)  # This will change
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Get sample data for extracting traits from text expedition."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--expedition-dir",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Place expedition files in this directory.""",
    )

    arg_parser.add_argument(
        "--ocr-set",
        required=True,
        metavar="NAME",
        help="""Use this OCR output.""",
    )

    arg_parser.add_argument(
        "--min-words",
        default=10,
        type=int,
        metavar="COUNT",
        help="""A label must have this many words to make it into the expedition.""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Sample this many labels.""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run. Enclose them in quotes.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
