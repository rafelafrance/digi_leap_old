#!/usr/bin/env python3
"""Convert training labels into YOLO7 format."""
import argparse
import textwrap
from pathlib import Path

from pylib.finder.yolo import export_yolo
from traiter.pylib import log


def main():
    log.started()
    args = parse_args()
    export_yolo.build(args)
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
        "--yolo-dir",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Save YOLO formatted data to this directory.""",
    )

    arg_parser.add_argument(
        "--train-set",
        metavar="NAME",
        required=True,
        help="""Which labels to use.""",
    )

    arg_parser.add_argument(
        "--image-size",
        type=int,
        metavar="INT",
        default=640,
        help="""Resize images to this height & width in pixels.
            (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
