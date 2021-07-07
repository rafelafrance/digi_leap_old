"""OCR images."""

import csv
from io import StringIO

import easyocr
import pytesseract
from PIL import Image

from digi_leap.const import CHAR_BLACKLIST, TESS_CONFIG
from digi_leap.util import to_opencv

EASY_OCR = easyocr.Reader(["en"])


def tesseract_engine(image: Image) -> list[dict]:
    """OCR the image with tesseract."""
    results = []
    raw = pytesseract.image_to_data(image, config=TESS_CONFIG)
    with StringIO(raw) as in_file:
        rows = [r for r in csv.DictReader(in_file, delimiter="\t")]
        if len(rows) < 5:   # OCR returned nothing
            return []
        for row in rows:
            conf = float(row["conf"])
            if conf < 0:  # Is an outer box that surrounds inner boxes
                continue
            left = int(row["left"])
            top = int(row["top"])
            results.append({
                "text": row["text"],
                "conf": conf / 100.0,
                "left": left,
                "top": top,
                "right": left + int(row["width"]) - 1,
                "bottom": top + int(row["height"]) - 1,
            })
    return results


def easyocr_engine(image: Image) -> list[dict]:
    """OCR the image with easyOCR."""
    results = []
    image = to_opencv(image)
    raw = EASY_OCR.readtext(image, blocklist=CHAR_BLACKLIST)
    for item in raw:
        pos = item[0]
        results.append({
            "text": item[1],
            "conf": item[2],
            "left": pos[0][0],
            "top": pos[0][1],
            "right": pos[1][0],
            "bottom": pos[2][1],
        })
    return results


def ocr_label(image: Image) -> dict:
    """OCR the image."""
    results = {
        "tesseract": tesseract_engine(image),
        "easyocr": easyocr_engine(image),
    }
    return results
