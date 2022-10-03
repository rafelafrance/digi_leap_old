#!/usr/bin/env python3
"""Create a new dataset for YOLO inference."""
import argparse
import textwrap
from pathlib import Path

from pylib import log
from pylib.finder.yolo import inference_prepare_yolo


def main():
    log.started()
    args = parse_args()
    inference_prepare_yolo.build(args)
    log.finished()


def parse_args():
    description = """Create images and data for YOLO inference."""

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
        help="""Save YOLO formatted images to this directory.""",
    )

    arg_parser.add_argument(
        "--sheet-set",
        required=True,
        metavar="NAME",
        help="""Create this sheet set.""",
    )

    arg_parser.add_argument(
        "--image-size",
        type=int,
        metavar="INT",
        default=640,
        help="""Resize images to this height & width in pixels.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=float,
        default=3000,
        help="""Sample this many sheets. (default: %(default)s)""",
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
