"""OCR a set of labels."""

import csv
import logging
import os
from argparse import Namespace
from multiprocessing import Pool
from os.path import basename, join, splitext

from PIL import Image
from tqdm import tqdm

import digi_leap.pylib.ocr as ocr


def ocr_labels(args: Namespace) -> None:
    """OCR the label images."""
    labels = filter_labels(args.prepared_dir, args.glob, args.limit)

    os.makedirs(args.output_dir, exist_ok=True)

    if args.ocr_engine == "tesseract":
        ocr_tesseract(labels, args.output_dir, args.cpus, args.batch_size)

    elif args.ocr_engine == "easyocr":
        ocr_easyocr(labels, args.output_dir)


def filter_labels(prepared_label_dir, image_filter, limit):
    """Filter labels that do not meet argument criteria."""
    logging.info("filtering labels")
    paths = sorted(prepared_label_dir.glob(image_filter))
    paths = [str(p) for p in paths]
    paths = paths[:limit] if limit else paths
    return paths


def ocr_tesseract(labels, tesseract_dir, cpus, batch_size):
    """OCR the labels with tesseract."""
    logging.info("OCR with Tesseract")

    batches = [labels[i:i + batch_size] for i in range(0, len(labels), batch_size)]

    with Pool(processes=cpus) as pool, tqdm(total=len(batches)) as bar:
        results = [
            pool.apply_async(
                tesseract_batch,
                (b, tesseract_dir),
                callback=lambda _: bar.update(),
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
    # Because EasyOCR uses the GPU I cannot use subprocesses on a laptop :(
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
