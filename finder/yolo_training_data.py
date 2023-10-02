#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import log
from pylib.yolo import yolo_prepare


def main():
    log.started()
    args = parse_args()
    yolo_prepare.build(args)
    log.finished()


def parse_args():
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Prepare label data into a format for YOLO training data.
            Required CSV columns:
                * "path": A path to the herbarium sheet image.
                * "class": The label class in text format.
                * "left": The label's left pixel.
                * "top": The label's top pixel.
                * "right": The label's right pixel.
                * "bottom": The label's bottom pixel.
            If the class is empty then the sheet has no labels.
            """
        ),
    )

    arg_parser.add_argument(
        "--label-csv",
        type=Path,
        metavar="PATH",
        required=True,
        help="""A CSV file containing all of the label information for
            training a YOLO model.""",
    )

    arg_parser.add_argument(
        "--yolo-images",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Save YOLO formatted images to this directory.""",
    )

    arg_parser.add_argument(
        "--yolo-labels",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Save YOLO formatted label information to this directory.""",
    )

    arg_parser.add_argument(
        "--yolo-size",
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
