#!/usr/bin/env python3
"""OCR a set of labels."""
import argparse
import itertools
import textwrap
import warnings
from datetime import datetime
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from .pylib import db
from .pylib import ocr
from .pylib.label_transforms import transform_label

ENGINE = {
    "tesseract": ocr.tesseract_engine,
    "easy": ocr.easyocr_engine,
}


def ocr_labels(args: argparse.Namespace) -> None:
    """OCR the label images."""
    db.create_ocr_table(args.database)

    sheets = get_sheet_labels(
        args.database,
        args.limit,
        args.classes,
        args.ruler_ratio,
        args.keep_n_largest,
    )

    with warnings.catch_warnings():  # Turn off EXIF warnings
        warnings.filterwarnings("ignore", category=UserWarning)

        for path, labels in tqdm(sheets.items()):
            sheet = Image.open(path)
            batch: list[dict] = []

            for lb in labels:
                label = sheet.crop(
                    (
                        lb["label_left"],
                        lb["label_top"],
                        lb["label_right"],
                        lb["label_bottom"],
                    )
                )

                for pipeline in args.pipelines:
                    image = transform_label(pipeline, label)

                    for engine in args.ocr_engines:
                        results = ENGINE[engine](image)
                        if results:
                            for result in results:
                                result |= {
                                    "label_id": lb["label_id"],
                                    "ocr_run": args.ocr_run,
                                    "engine": engine,
                                    "pipeline": pipeline,
                                }
                            batch += results

            db.insert_ocr(args.database, batch)


def get_sheet_labels(database, limit, classes, ruler_ratio, keep_n_largest):
    """get the labels for each herbarium sheet and filter them."""
    sheets = {}
    labels = db.select_labels(database)
    labels = sorted(labels, key=lambda lb: (lb["path"], lb["offset"]))
    grouped = itertools.groupby(labels, lambda lb: lb["path"])

    for path, labels in grouped:
        labels = list(labels)

        if classes:
            labels = [lb for lb in labels if lb["class"] in classes]

        if ruler_ratio > 0.0 and labels:
            labels = filter_rulers(labels, ruler_ratio)

        if keep_n_largest and labels:
            labels = filter_n_largest(labels, keep_n_largest)

        if labels:
            sheets[path] = labels

    if limit:
        sheets = {p: lb for i, (p, lb) in enumerate(sheets.items()) if i < limit}

    return sheets


def filter_rulers(labels, ruler_ratio):
    """Remove rulers from the labels."""
    new = []
    for lb in labels:
        d1 = lb["label_right"] - lb["label_left"]
        d2 = lb["label_bottom"] - lb["label_top"]
        d1, d2 = (d1, d2) if d1 > d2 else (d2, d1)
        if d1 / d2 <= ruler_ratio:
            new.append(lb)
    return new


def filter_n_largest(labels, keep_n_largest):
    """Keep the N largest labels for each sheet."""
    labels = sorted(
        labels,
        reverse=True,
        key=lambda lb: (
            (lb["label_right"] - lb["label_left"])
            * (lb["label_bottom"] - lb["label_top"])
        ),
    )
    return labels[:keep_n_largest]


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """OCR images of labels."""

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
        "--ocr-run",
        default=default,
        help="""Name the label finder run. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--pipelines",
        choices=["deskew", "binarize", "denoise"],
        default=["deskew", "binarize"],
        type=str,
        nargs="*",
        help="""Pipelines of image transformations that help with the OCR process.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--ocr-engines",
        choices=["tesseract", "easy"],
        default=["tesseract", "easy"],
        type=str,
        nargs="*",
        help="""Which OCR engines to use. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--classes",
        choices=["Barcode", "Handwritten", "Typewritten", "Both"],
        default=["Typewritten"],
        type=str,
        nargs="*",
        help="""Keep labels if they fall into any of these categories.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--ruler-ratio",
        type=float,
        help="""Consider a label to be a ruler if the height:width
            (or width:height) ratio is above this.""",
    )

    arg_parser.add_argument(
        "--keep-n-largest",
        type=int,
        help="""Keep the N largest labels for each sheet.""",
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
    ocr_labels(ARGS)
