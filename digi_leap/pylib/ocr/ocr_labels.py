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
from ..builder import label_builder
from ..builder.line_align import char_sub_matrix as subs
from ..builder.line_align import line_align_py  # noqa
from ..builder.spell_well import SpellWell
from ..db import db


class Ensemble:
    def __init__(self, args):
        self.none_easyocr = args.none_easyocr
        self.none_tesseract = args.none_tesseract
        self.deskew_easyocr = args.deskew_easyocr
        self.deskew_tesseract = args.deskew_tesseract
        self.binarize_easyocr = args.binarize_easyocr
        self.binarize_tesseract = args.binarize_tesseract
        self.denoise_easyocr = args.denoise_easyocr
        self.denoise_tesseract = args.denoise_tesseract
        self.post_process = args.post_process

        matrix = subs.select_char_sub_matrix(char_set="default")
        self.line_align = line_align_py.LineAlign(matrix)
        self.spell_well = SpellWell()

    @property
    def need_deskew(self):
        return self.deskew_easyocr or self.deskew_tesseract

    @property
    def need_binarize(self):
        return self.binarize_easyocr or self.binarize_tesseract

    @property
    def need_denoise(self):
        return self.denoise_easyocr or self.denoise_tesseract

    @property
    def pipeline(self):
        pipes = []
        if self.none_easyocr:
            pipes.append("[,easyocr]")
        if self.none_tesseract:
            pipes.append("[,tesseract]")
        if self.deskew_easyocr:
            pipes.append("[deskew,easyocr]")
        if self.deskew_tesseract:
            pipes.append("[deskew,tesseract]")
        if self.binarize_easyocr:
            pipes.append("[binarize,easyocr]")
        if self.binarize_tesseract:
            pipes.append("[binarize,tesseract]")
        if self.denoise_easyocr:
            pipes.append("[denoise,easyocr]")
        if self.denoise_tesseract:
            pipes.append("[denoise,tesseract]")
        if self.post_process:
            pipes.append("[post_process]")
        return ",".join(pipes)

    def run(self, image):
        lines = [ln for ln in self.ocr(image)]
        lines = label_builder.filter_lines(lines, self.line_align)
        text = self.line_align.align(lines)
        text = label_builder.consensus(text)
        if self.post_process:
            text = label_builder.post_process_text(text, self.spell_well)
        return text

    def ocr(self, image):
        deskew = lt.transform_label("deskew", image) if self.need_deskew else None
        binary = lt.transform_label("binarize", image) if self.need_binarize else None
        denoise = lt.transform_label("denoise", image) if self.need_denoise else None

        lines = []
        if self.none_easyocr:
            lines.append(ocr_runner.easy_text(image))
        if self.none_tesseract:
            lines.append(ocr_runner.tess_text(image))
        if self.deskew_easyocr:
            lines.append(ocr_runner.easy_text(deskew))
        if self.deskew_tesseract:
            lines.append(ocr_runner.tess_text(deskew))
        if self.binarize_easyocr:
            lines.append(ocr_runner.easy_text(binary))
        if self.binarize_tesseract:
            lines.append(ocr_runner.tess_text(binary))
        if self.denoise_easyocr:
            lines.append(ocr_runner.easy_text(denoise))
        if self.denoise_tesseract:
            lines.append(ocr_runner.tess_text(denoise))
        return lines


def ocr_labels(args: argparse.Namespace) -> None:
    ensemble = Ensemble(args)

    with db.connect(args.database) as cxn:
        # run_id = db.insert_run(cxn, args)

        db.canned_delete(cxn, "ocr_texts", ocr_set=args.ocr_set)

        sheets = get_sheet_labels(
            cxn, args.classes, args.label_set, args.label_conf, args.limit
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

                    text = ensemble.run(label)
                    batch.append(
                        {
                            "label_id": lb["label_id"],
                            "ocr_set": args.ocr_set,
                            "pipeline": ensemble.pipeline,
                            "ocr_text": text,
                        }
                    )
                db.canned_insert(cxn, "ocr_texts", batch)

            # db.update_run_finished(cxn, run_id)


def get_sheet_labels(cxn, classes, label_set, label_conf, limit):
    sheets = {}
    labels = db.canned_select(
        cxn, "labels", label_set=label_set, label_conf=label_conf, limit=limit
    )
    labels = sorted(labels, key=lambda lb: lb["path"])
    grouped = itertools.groupby(labels, lambda lb: lb["path"])

    for path, labels in grouped:
        labels = list(labels)

        if classes:
            labels = [lb for lb in labels if lb["class"] in classes]

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
