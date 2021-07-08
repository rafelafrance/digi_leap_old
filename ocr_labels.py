#!/usr/bin/env python
"""OCR  a set of labels."""

import json
import multiprocessing
import os
import textwrap
from argparse import ArgumentParser, Namespace
from os import makedirs
from pathlib import Path

from PIL import Image

from digi_leap.label_transforms import get_script, transform_label
from digi_leap.log import finished, started
from digi_leap.ocr import ocr_label

BATCH_SIZE = 100


def ocr_labels(args: Namespace) -> None:
    """OCR the label images."""
    makedirs(args.output_dir, exist_ok=True)

    paths = [str(p) for p in sorted(args.label_dir.glob("*"))]
    batches = [paths[i:i + BATCH_SIZE] for i in range(0, len(paths), BATCH_SIZE)]

    with multiprocessing.Pool(processes=args.cpus) as pool:
        results = [pool.apply_async(process_batch, (b, vars(args))) for b in batches]
        results = [r.get() for r in results]


def process_batch(batch, args):
    """OCR a batch of labels."""

    script = get_script()
    for path in batch:
        in_path = Path(path)
        out_path = args["output_dir"] / f"{in_path.stem}.json"

        if out_path.exists() and not args["restart"]:
            continue

        image = Image.load(in_path)
        image = transform_label(image)
        results = ocr_label(image)
        results["script"] = script

        with open(out_path, "w") as out_file:
            json.dump(results, out_file, indent=True)


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
        OCR images of labels.

        Take all images in the input --label-dir, OCR them and output the results
        to the --output-dir. The file name stems of the output files echo the file
        name stems of the input images. The input label images should be cut out
        of the images of the specimens first.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--label-dir",
        required=True,
        type=Path,
        help="""The directory containing input labels.""",
    )

    arg_parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="""The directory to output OCR results.""",
    )

    arg_parser.add_argument(
        "--restart",
        action="store_true",
        help="""If selected this will overwrite existing output files.""",
    )

    cpus = max(1, min(10, os.cpu_count() - 4))
    arg_parser.add_argument(
        "--cpus",
        type=int,
        default=cpus,
        help="""How many CPUs to use. (default %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    ocr_labels(ARGS)

    finished()
