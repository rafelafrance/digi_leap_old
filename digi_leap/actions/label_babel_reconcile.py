#!/usr/bin/env python3
"""Reconcile data from a Label Babel expedition."""

import textwrap
from argparse import ArgumentParser, Namespace
from pathlib import Path

from digi_leap.pylib.config import Config
import digi_leap.pylib.log as log
import digi_leap.pylib.reconcile as recon


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

    defaults = Config().module_defaults()

    arg_parser.add_argument(
        "--unreconciled-csv",
        default=defaults["unreconciled_csv"],
        type=Path,
        help="""The unreconciled input CSV. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--sheet-dir",
        default=defaults["sheets_dir"],
        type=Path,
        help="""Herbarium sheet images are in this directory. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--reconciled-jsonl",
        default=defaults["reconciled_jsonl"],
        type=Path,
        help="""The reconciled output as a JSONL file. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    recon.reconcile(ARGS.unreconciled_csv, ARGS.image_dir, ARGS.reconciled_jsonl)

    log.finished()
