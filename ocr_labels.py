#!/usr/bin/env python
"""OCR  a set of labels."""

import multiprocessing
import os
import textwrap
from argparse import ArgumentParser, Namespace
from os import makedirs
from pathlib import Path
from typing import Optional

import numpy.typing as npt
from PIL import Image
from skimage import color, io

from digi_leap.label_transforms import transform_label
from digi_leap.log import finished, started

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

    for path in batch:
        path = Path(path)

        if path.exists() and not args["restart"]:
            continue

        image = Image.load(path)
        image = transform_label(image)
        # Read image
        # Process image
        # OCR image tesseract
        # OCR image easyOCR
        # Write results


def output_label(
    args: Namespace,
    image_path: Path,
    label: Optional[npt.ArrayLike],
    suffix: str,
) -> Optional[npt.ArrayLike]:
    """Output data in the specified format."""
    dir_ = args.data_dir if suffix == ".tsv" else args.text_dir
    if not dir_:
        return label

    path = dir_ / f"{image_path.stem}{suffix}"
    if path.exists() and not args.restart:
        return label

    if not label:
        label = prepare_image(image_path)

    info = label.ocr_data() if suffix == ".tsv" else label.ocr_text()
    info = info.strip()
    with open(path, "w") as out_file:
        out_file.write(info)
        out_file.write("\n")

    return label


def prepare_image(path: Path) -> npt.ArrayLike:
    """Turn an image of a label into text."""
    label = io.imread(str(path))
    label = color.rgb2gray(label)
    # label.deskew()
    # label.binarize()
    #
    # if lines := label.find_horizontal_lines(line_gap=5):
    #     label.remove_horiz_lines(lines, window=20, threshold=2)
    #
    # if lines := label.find_vertical_lines(line_gap=5):
    #     label.remove_vert_lines(lines, window=20, threshold=2)

    return label


def make_dirs(args: Namespace) -> None:
    """Create output directories."""
    if args.data_dir:
        makedirs(args.data_dir, exist_ok=True)
    if args.text_dir:
        makedirs(args.text_dir, exist_ok=True)


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
