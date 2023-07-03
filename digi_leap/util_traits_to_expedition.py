#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib.ocr.is_correction_needed import build_expedition
from traiter.pylib import log


def main():
    log.started()
    args = parse_args()
    build_expedition.build_2_files(args)
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
        help="""Output the results from this OCR set.""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Sample this many labels.""",
    )

    arg_parser.add_argument(
        "--score-cutoff",
        type=float,
        default=0.7,
        metavar="FRACTION",
        help="""Only keep labels if their score is this or more.
            The score is between 0.0 and 1.0. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--length-cutoff",
        type=int,
        default=10,
        metavar="LENGTH",
        help="""Only keep labels if they have at least this many words.
            (default: %(default)s)""",
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
