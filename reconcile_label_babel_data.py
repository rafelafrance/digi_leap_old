#!/usr/bin/env python
"""Reconcile data from a Label Babel expedition."""

import textwrap
from argparse import ArgumentParser, Namespace
from pathlib import Path

from digi_leap.log import finished, started
from digi_leap.reconcile import reconcile


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
        Reconcile data from a Label Babel expedition.

        This script merges bounding boxes and label types from unreconciled Label Babel
        classifications. We have to figure out which bounding boxes refer to which
        labels on the herbarium sheet and then merge them to find a single "best"
        bounding box.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--unreconciled-csv",
        required=True,
        type=Path,
        help="""The unreconciled input CSV.""",
    )

    arg_parser.add_argument(
        "--image-dir",
        required=True,
        type=Path,
        help="""Read training images from this directory.""",
    )

    arg_parser.add_argument(
        "--reconciled-jsonl",
        required=True,
        type=Path,
        help="""The reconciled output as a JSONL file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    reconcile(ARGS.unreconciled_csv, ARGS.image_dir, ARGS.reconciled_jsonl)

    finished()
