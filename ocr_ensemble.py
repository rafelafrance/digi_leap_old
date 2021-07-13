#!/usr/bin/env python
"""Combine OCR results into an ensemble for each label."""

import textwrap
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from pathlib import Path

import pandas as pd

from digi_leap.log import finished, started


GLOB = "*.csv"


def build_ensembles(args):
    """Group OCR output paths by label."""
    paths = group_files(args)
    for label, csv_paths in paths.items():
        boxes = get_boxes(csv_paths)
        boxes = filter_boxes(boxes)
        ensemble = group_boxes(label, boxes)
        write_file(args, label, ensemble)


def group_files(args):
    """Find files that represent then same label and group them."""
    paths = defaultdict(list)
    for ocr_dir in args.ocr_dir:
        paths = ocr_dir.glob(GLOB)
        for path in paths:
            label = path.stem
            paths[label].append(path)
    return paths


def get_boxes(paths):
    """Get all the bounding boxes from the paths."""
    boxes = []
    for path in paths:
        boxes.append(pd.read_csv(path))
    return boxes


def filter_boxes(paths):
    """Remove bounding boxes that seem to contain noise."""


def group_boxes(label, paths):
    """Group all bounding boxes in the label."""
    pass


def write_file(args, label, ensemble):
    """Write the ensemble to a file."""
    path = args.ensemble_dir / f"{label}.csv"
    ensemble.to_csv(path, index=False)


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
        Combine OCR results into an ensemble for each label.

        Take the output of multiple OCR runs and combine them into an
        ensemble of outputs. We match the file names of each OCR run to
        each other, and then combine the bounding box results for each
        label. Note: This script depends on the file name between OCR runs
        being the same.
        """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--ocr-dir",
        required=True,
        type=Path,
        nargs="+",
        help="""The directory containing OCR output.""",
    )

    arg_parser.add_argument(
        "--ensemble-dir",
        type=Path,
        help="""Output the OCR ensembles to this directory.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    build_ensembles(ARGS)

    finished()
