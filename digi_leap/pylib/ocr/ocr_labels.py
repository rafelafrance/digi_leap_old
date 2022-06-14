"""OCR a set of labels."""
import argparse
import itertools
import warnings

import torch
from PIL import Image
from tqdm import tqdm

from . import label_transformer as lt
from . import ocr_runner
from .. import box_calc
from ..db import db

ENGINE = {
    "tesseract": ocr_runner.tesseract_engine,
    "easy": ocr_runner.easyocr_engine,
}


def ocr_labels(args: argparse.Namespace) -> None:
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        db.execute(cxn, "delete from ocr where ocr_set = ?", (args.ocr_set,))

        sheets = get_sheet_labels(cxn, args.classes, args.label_set, args.label_conf)

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
                            results = [
                                r for r in ENGINE[engine](image) if r["ocr_text"]
                            ]
                            for result in results:
                                batch.append(
                                    result
                                    | {
                                        "label_id": lb["label_id"],
                                        "ocr_set": args.ocr_set,
                                        "engine": engine,
                                        "pipeline": pipeline,
                                    }
                                )

                db.canned_insert("ocr", cxn, batch)

        db.update_run_finished(cxn, run_id)


def get_sheet_labels(cxn, classes, label_set, label_conf):
    sheets = {}
    labels = db.canned_select("labels", cxn, label_set=label_set)
    labels = sorted(labels, key=lambda lb: (lb["path"], lb["offset"]))
    grouped = itertools.groupby(labels, lambda lb: lb["path"])

    for path, labels in grouped:
        labels = list(labels)

        if classes:
            labels = [lb for lb in labels if lb["class"] in classes]

        labels = [lb for lb in labels if lb["label_conf"] >= label_conf]
        labels = remove_overlapping_labels(labels)

        if labels:
            sheets[path] = labels

    return sheets


def remove_overlapping_labels(labels):
    boxes = [
        [lb["label_left"], lb["label_top"], lb["label_right"], lb["label_bottom"]]
        for lb in labels
    ]
    boxes = torch.tensor(boxes)
    boxes = box_calc.small_box_suppression(boxes, threshold=0.4)
    return [lb for i, lb in enumerate(labels) if i in boxes]
