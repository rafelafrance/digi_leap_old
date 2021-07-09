#!/usr/bin/env python
"""OCR a set of labels."""

import json
import logging
import os
import textwrap
from argparse import ArgumentParser, Namespace
from multiprocessing import Pool
from os import makedirs
from os.path import basename, join, splitext
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from digi_leap.log import finished, started
from digi_leap.ocr import easyocr_engine, tesseract_engine

BATCH_SIZE = 10


def ocr_labels(args: Namespace) -> None:
    """OCR the label images."""
    labels = filter_labels(args)

    if args.tesseract_dir:
        makedirs(args.tesseract_dir, exist_ok=True)
        ocr_tesseract(labels, args)

    if args.easyocr_dir:
        makedirs(args.easyocr_dir, exist_ok=True)
        ocr_easyocr(labels, args)


def filter_labels(args):
    """Filter labels that do not meet argument criteria."""
    logging.info("filtering labels")
    paths = sorted(args.label_dir.glob(args.image_filter))
    paths = [{"label": str(p)} for p in paths]
    paths = paths[: args.limit] if args.limit else paths
    return paths


def ocr_tesseract(labels, args):
    """OCR the labels with tesseract."""
    logging.info("OCR with Tesseract")

    batches = [labels[i:i + BATCH_SIZE] for i in range(0, len(labels), BATCH_SIZE)]

    with Pool(processes=args.cpus) as pool, tqdm(total=len(batches)) as bar:
        results = [
            pool.apply_async(
                tesseract_batch, (b, vars(args)), callback=lambda _: bar.update(1)
            )
            for b in batches
        ]
        _ = [r.get() for r in results]


def tesseract_batch(batch, args):
    """OCR one set of labels with tesseract."""
    for label in batch:
        image = Image.open(label["label"])
        results = tesseract_engine(image)

        path = splitext(basename(label["label"]))[0]
        path = join(args["tesseract_dir"], f"{path}.tesseract.json")

        with open(path, "w") as json_file:
            json.dump(results, json_file, indent=True)


def ocr_easyocr(labels, args):
    """OCR the label with easyocr."""
    # Because EasyOCR uses the GPU we cannot use subprocesses :(
    logging.info("OCR with EasyOCR")
    for label in tqdm(labels):
        image = Image.open(label["label"])
        results = easyocr_engine(image)

        path = splitext(basename(label["label"]))[0]
        path = join(args.easyocr_dir, f"{path}.easyocr.json")

        with open(path, "w") as json_file:
            json.dump(results, json_file, indent=True)


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
        OCR images of labels.

        Take all images in the input --label-dir, OCR them, and output the results
        into either (or both) the --tesseract-dir or the --easyocr-dir. The output
        directory determines which OCR engine is used. The output file names
        echo the file name stems of the input images. Make sure that the input
        label images are prepared for OCR.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--label-dir",
        required=True,
        type=Path,
        help="""The directory containing OCR ready labels.""",
    )

    arg_parser.add_argument(
        "--tesseract-dir",
        type=Path,
        help="""Output the Tesseract OCR results to this directory.""",
    )

    arg_parser.add_argument(
        "--easyocr-dir",
        type=Path,
        help="""Output the EasyOCR OCR results to this directory.""",
    )

    cpus = max(1, min(10, os.cpu_count() - 8))
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
