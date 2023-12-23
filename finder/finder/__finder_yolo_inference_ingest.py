#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import log

from old import inference_ingest_yolo


def main():
    log.started()
    args = parse_args()
    inference_ingest_yolo.ingest(args)
    log.finished()


def parse_args():
    description = """Read in YOLO inference results."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--yolo-dir",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Read YOLO results from this directory.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
