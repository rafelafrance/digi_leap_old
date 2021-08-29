#!/usr/bin/env python
"""OCR a set of labels."""

import csv
import logging
import os
import textwrap
from argparse import ArgumentParser, Namespace
from multiprocessing import Pool
from os.path import basename, join, splitext
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from pylib.config import Configs
import pylib.const as const
import pylib.log as log
import pylib.ocr as ocr


def ocr_labels(args: Namespace) -> None:
    """OCR the label images."""
    labels = filter_labels(args.prepared_dir, args.image_filter, args.limit)

    if args.tesseract_dir:
        os.makedirs(args.tesseract_dir, exist_ok=True)
        ocr_tesseract(labels, args.tesseract_dir, args.cpus)

    if args.easyocr_dir:
        os.makedirs(args.easyocr_dir, exist_ok=True)
        ocr_easyocr(labels, args.easyocr_dir)


def filter_labels(prepared_dir, image_filter, limit):
    """Filter labels that do not meet argument criteria."""
    logging.info("filtering labels")
    paths = sorted(prepared_dir.glob(image_filter))
    paths = [str(p) for p in paths]
    paths = paths[: limit] if limit else paths
    return paths


def ocr_tesseract(labels, tesseract_dir, cpus):
    """OCR the labels with tesseract."""
    logging.info("OCR with Tesseract")

    batches = [labels[i:i + const.PROC_BATCH]
               for i in range(0, len(labels), const.PROC_BATCH)]

    with Pool(processes=cpus) as pool, tqdm(total=len(batches)) as bar:
        results = [
            pool.apply_async(
                tesseract_batch, (b, tesseract_dir), callback=lambda _: bar.update()
            )
            for b in batches
        ]
        _ = [r.get() for r in results]


def tesseract_batch(batch, tesseract_dir):
    """OCR one set of labels with tesseract."""
    for label in batch:
        path = name_output_file(tesseract_dir, label)
        image = Image.open(label)
        df = ocr.tesseract_dataframe(image)
        df.to_csv(path, index=False)


def ocr_easyocr(labels, easyocr_dir):
    """OCR the label with easyocr."""
    # Because EasyOCR uses the GPU we cannot use subprocesses :(
    logging.info("OCR with EasyOCR")
    for label in tqdm(labels):
        image = Image.open(label)
        results = ocr.easyocr_engine(image)

        path = name_output_file(easyocr_dir, label)
        to_csv(path, results)


def name_output_file(dir_path, label):
    """Generate the output file name."""
    path = splitext(basename(label))[0]
    path = join(dir_path, f"{path}.csv")
    return path


def to_csv(path, results):
    """Write the results to a CSV file."""
    headers = "conf left top right bottom text".split()

    with open(path, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)

        for box in results:
            writer.writerow(
                [
                    box["conf"],
                    box["left"],
                    box["top"],
                    box["right"],
                    box["bottom"],
                    box["text"],
                ]
            )


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

    defaults = Configs().module_defaults()

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

    arg_parser.add_argument(
        "--image-filter",
        type=str,
        default="*.jpg",
        help="""Filter files in the --label-dir with this. (default %(default)s)""",
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

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    ocr_labels(ARGS)

    log.finished()
