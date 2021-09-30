"""OCR a set of labels."""

import csv
import itertools
import warnings
from argparse import Namespace
from datetime import datetime

from PIL import Image
from tqdm import tqdm

import digi_leap.pylib.db as db
import digi_leap.pylib.ocr as ocr
from digi_leap.pylib.label_transforms import LabelTransform, transform_label

ENGINE = {
    "tesseract": ocr.tesseract_engine,
    "easy": ocr.easyocr_engine,
}


def ocr_labels(args: Namespace) -> None:
    """OCR the label images."""
    db.create_ocr_results_table(args.database)

    sheets = get_sheet_labels(
        args.database, args.limit, args.classes, args.ruler_ratio, args.keep_n_largest,
    )

    run = datetime.now().isoformat(sep="_", timespec="seconds")

    with warnings.catch_warnings():  # Turn off EXIF warnings
        warnings.filterwarnings("ignore", category=UserWarning)

        for path, labels in tqdm(sheets.items()):
            sheet = Image.open(path)
            batch = []

            for lb in labels:
                label = sheet.crop((lb["left"], lb["top"], lb["right"], lb["bottom"]))

                for pipeline in args.pipelines:
                    image = transform_label(pipeline, label)

                    for engine in args.ocr_engines:
                        results = ENGINE[engine](image)
                        if results:
                            for result in results:
                                result |= {
                                    "run": run,
                                    "path": path,
                                    "offset": lb["offset"],
                                    "engine": engine,
                                    "pipeline": pipeline,
                                }
                            batch += results

            db.insert_ocr_results(args.database, batch)


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
        d1, d2 = (lb["right"] - lb["left"]), (lb["bottom"] - lb["top"])
        d1, d2 = (d1, d2) if d1 > d2 else (d2, d1)
        if d1 / d2 <= ruler_ratio:
            new.append(lb)
    return new


def filter_n_largest(labels, keep_n_largest):
    """Keep the N largest labels for each sheet."""
    labels = sorted(
        labels,
        reverse=True,
        key=lambda lb: (lb["right"] - lb["left"]) * (lb["bottom"] - lb["top"]),
    )
    return labels[:keep_n_largest]


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
