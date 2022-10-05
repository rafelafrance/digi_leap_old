#!/usr/bin/env python3
"""Convert YOLO results into Digi-Leap data."""
import argparse
import textwrap
from pathlib import Path

from pylib.finder.yolo import import_yolo
from traiter import log


def main():
    log.started()
    args = parse_args()
    import_yolo.load(args)
    log.finished()


def parse_args():
    description = """This script converts label training data into YOLOv7 format."""

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
        "--yolo-json",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Path to the YOLO results JSON file.""",
    )

    arg_parser.add_argument(
        "--train-set",
        metavar="NAME",
        required=True,
        help="""Which labels to use.""",
    )

    arg_parser.add_argument(
        "--test-set",
        metavar="NAME",
        required=True,
        help="""Name this label finder test set.""",
    )

    arg_parser.add_argument(
        "--image-size",
        type=int,
        metavar="INT",
        default=640,
        help="""Images were resized to this height & width in pixels.
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
