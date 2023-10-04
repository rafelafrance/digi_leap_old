#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import log
from pylib.yolo import yolo_to_labels


def main():
    log.started()
    args = parse_args()
    yolo_to_labels.to_labels(args)
    log.finished()


def parse_args():
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            This script converts YOLO results to label images.
            Required CSV columns:
                * "path": A path to the herbarium sheet image.
           """
        ),
    )

    arg_parser.add_argument(
        "--yolo-labels",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Directory containing the label predictions.""",
    )

    arg_parser.add_argument(
        "--sheet-csv",
        type=Path,
        metavar="PATH",
        required=True,
        help="""A CSV file containing all of the herbarium sheets paths fed to the
            YOLO model. It's OK to use the CSV from training --label-csv.""",
    )

    arg_parser.add_argument(
        "--label-dir",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Output the label images to this directory.""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    main()
