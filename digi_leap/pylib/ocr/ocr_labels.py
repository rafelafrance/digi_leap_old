"""OCR a set of labels."""
import argparse
import itertools
import sqlite3
import warnings

from PIL import Image
from tqdm import tqdm

from . import engine_runner
from . import label_transformer as lt
from .. import db

ENGINE = {
    "tesseract": engine_runner.tesseract_engine,
    "easy": engine_runner.easyocr_engine,
}


def ocr_labels(args: argparse.Namespace) -> None:
    """OCR the label images."""
    run_id = db.insert_run(args)

    with sqlite3.connect(args.database) as cxn:
        cxn.execute("""delete from ocr where ocr_set = ?""", (args.ocr_set,))

    db.create_ocr_table(args.database)

    sheets = get_sheet_labels(
        args.database, args.limit, args.classes, args.label_set, args.label_conf
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
                    image = lt.transform_label(pipeline, label)

                    for engine in args.ocr_engines:
                        results = ENGINE[engine](image)
                        if results:
                            for result in results:
                                result |= {
                                    "label_id": lb["label_id"],
                                    "ocr_set": args.ocr_set,
                                    "engine": engine,
                                    "pipeline": pipeline,
                                }
                            batch += results

                db.insert_ocr(args.database, args.ocr_set, batch)

    db.update_run_finished(args.database, run_id)


def get_sheet_labels(database, limit, classes, label_set, label_conf):
    """get the labels for each herbarium sheet and filter them."""
    sheets = {}
    labels = db.select_labels(database, label_set=label_set)
    labels = sorted(labels, key=lambda lb: (lb["path"], lb["offset"]))
    grouped = itertools.groupby(labels, lambda lb: lb["path"])

    for path, labels in grouped:
        labels = list(labels)

        if classes:
            labels = [lb for lb in labels if lb["class"] in classes]

        labels = [lb for lb in labels if lb["label_conf"] >= label_conf]

        if labels:
            sheets[path] = labels

    if limit:
        sheets = {p: lb for i, (p, lb) in enumerate(sheets.items()) if i < limit}

    return sheets
