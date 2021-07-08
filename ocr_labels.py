#!/usr/bin/env python
"""OCR  a set of labels."""

import json
import multiprocessing
import os
import textwrap
from argparse import ArgumentParser, Namespace
from itertools import chain
from os import makedirs
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from digi_leap.label_transforms import DEFAULT_PIPELINE, transform_label
from digi_leap.log import finished, started
from digi_leap.ocr import easyocr_engine, tesseract_engine

BATCH_SIZE = 100
PIPELINE = DEFAULT_PIPELINE


def ocr_labels(args: Namespace) -> None:
    """OCR the label images."""
    makedirs(args.output_dir, exist_ok=True)

    labels = filter_labels(args)

    batches = [labels[i:i + BATCH_SIZE] for i in range(0, len(labels), BATCH_SIZE)]

    with TemporaryDirectory() as temp_dir:
        transform_labels(batches, args, temp_dir)
        labels = ocr_tesseract(batches, args, temp_dir)
        labels = ocr_easyocr(labels, args, temp_dir)
    output_ocr_results(labels, args)


def filter_labels(args):
    """Filter labels that do not meet argument criteria."""
    paths = sorted(args.label_dir.glob(args.image_filter))
    paths = [{"path": str(p), "json": f"{p.stem}.json"} for p in paths]
    paths = [p for p in paths if not p["json"].exists or args.restart]
    paths = paths[: args.limit] if args.limit else paths
    return paths


def transform_labels(batches, args, temp_dir):
    """Perform the label transformations before the OCR step(s)."""
    with multiprocessing.Pool(processes=args.cpus) as pool:
        _ = [
            pool.apply_async(transform_batch, (b, vars(args), temp_dir))
            for b in batches
        ]


def transform_batch(batch, args, temp_dir):
    """Perform the label transformations on a batch of labels."""
    for label in batch:
        image = Image.open(label["path"])
        image, actions = transform_label(PIPELINE, image)

        label["actions"] = actions

        temp_image = Path(temp_dir) / label["path"].name
        image.save(temp_image)


def ocr_tesseract(batches, args, temp_dir):
    """OCR the labels with tesseract."""
    with multiprocessing.Pool(processes=args.cpus) as pool:
        results = [
            pool.apply_async(tesseract_batch, (b, vars(args), temp_dir))
            for b in batches
        ]
        results = [r.get() for r in results]

    labels = list(chain.from_iterable(results))
    return labels


def tesseract_batch(batch, args, temp_dir):
    """OCR one set of labels with tesseract."""
    results = []
    for label in batch:
        image = Path(temp_dir) / label["path"].name
        label["tesseract"] = tesseract_engine(image)
        results.append(label)
    return results


def ocr_easyocr(labels, args, temp_dir):
    """OCR the label with easyocr."""
    # Because EasyOCR uses the GPU we cannot use subprocesses :(
    results = []
    for label in labels:
        image = Path(temp_dir) / label["path"].name
        label["easyocr"] = easyocr_engine(image)
        results.append(label)
    return results


def output_ocr_results(labels, args):
    """OCR the label with easyocr."""
    for label in labels:
        del label["json"]
        in_path = Path(label["path"])
        json_path = args.output_dir / f"{in_path.stem}.json"
        with open(json_path, "w") as json_file:
            json.dump(label, json_file, indent=True)


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

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many label images.""",
    )

    arg_parser.add_argument(
        "--image-filter",
        type=str,
        default="*.jpg",
        help="""Filter files in the --label-dir with this. (default %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    ocr_labels(ARGS)

    finished()
