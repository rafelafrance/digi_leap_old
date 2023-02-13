#!/usr/bin/env python3
"""Build an expedition to determine the quality of label finder output."""
import argparse
import textwrap
from pathlib import Path

from pylib.finder.rise_of_machines import build_expedition
from traiter.pylib import log


def main():
    log.started()
    args = parse_args()
    build_expedition.build(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Build an expedition to determine the quality of the
        label builder.

        Ths "Rise of Machines" expedition.
        """

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
        "--label-set",
        required=True,
        metavar="NAME",
        help="""Get labels from this label set.""",
    )

    arg_parser.add_argument(
        "--label-conf",
        type=float,
        default=0.25,
        help="""Use labels that have a confidence >= to this. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=float,
        default=3000,
        help="""Sample this many sheets. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--reduce-by",
        type=int,
        default=1,
        metavar="N",
        help="""Shrink images by this factor. (default: %(default)s)""",
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
