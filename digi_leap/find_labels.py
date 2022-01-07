#!/usr/bin/env python3
"""Use a trained model to cut out labels on herbarium sheets."""
import argparse
import textwrap
from datetime import datetime
from pathlib import Path

from .pylib.find_labels import find_labels


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """Use a model that finds labels on herbarium sheets (inference)."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Path to the digi-leap database.""",
    )

    default = datetime.now().isoformat(sep="_", timespec="seconds")
    arg_parser.add_argument(
        "--label-run",
        default=default,
        help="""Name the label finder run. (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--load-model",
        type=Path,
        help="""Path, to the current model for finding labels on a herbarium sheet.""",
    )

    arg_parser.add_argument(
        "--device",
        default="cuda",
        help="""Which GPU or CPU to use. (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--nms-threshold",
        type=float,
        default=0.3,
        help="""IoU overlap to use for non-maximum suppression.
            (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--sbs-threshold",
        type=float,
        default=0.95,
        help="""IoU overlap to use for small box suppression.
            (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    find_labels(ARGS)
