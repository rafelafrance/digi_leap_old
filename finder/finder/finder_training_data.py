#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import log
from pylib.yolo import training_data


def main():
    log.started()
    args = parse_args()
    training_data.build(args)
    log.finished()


def parse_args():
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Prepare label training data into a format for YOLO model training.
            Required CSV columns:
                * "path": A path to the herbarium sheet image.
                * "class": The label class in text format.
                * "left": The label's left most pixel.
                * "top": The label's top most pixel.
                * "right": The label's right most pixel.
                * "bottom": The label's bottom most pixel.
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
