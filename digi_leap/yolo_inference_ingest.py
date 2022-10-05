#!/usr/bin/env python3
"""Read in YOLO inference results."""
import argparse
import textwrap
from pathlib import Path

from pylib.finder.yolo import inference_ingest_yolo
from traiter import log


def main():
    log.started()
    args = parse_args()
    inference_ingest_yolo.ingest(args)
    log.finished()


def parse_args():
    description = """Read in YOLO inference results."""

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
        "--yolo-dir",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Read YOLO results from this directory.""",
    )

    arg_parser.add_argument(
        "--sheet-set",
        required=True,
        metavar="NAME",
        help="""Get sheet information from this sheet set.""",
    )

    arg_parser.add_argument(
        "--label-set",
        metavar="NAME",
        required=True,
        help="""Write labels to this set.""",
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
