"""OCR images."""

import csv
from io import StringIO

import easyocr
import numpy as np
import pytesseract
from PIL import Image

from digi_leap.const import CHAR_BLACKLIST, TESS_CONFIG

EASY_OCR = easyocr.Reader(["en"])

KEYS = """conf left top right bottom text""".split()


def tesseract_engine(image: Image) -> list[dict]:
    """OCR the image with tesseract."""
    results = []
    raw = pytesseract.image_to_data(image, config=TESS_CONFIG)
    with StringIO(raw) as in_file:
        rows = [r for r in csv.DictReader(in_file, delimiter="\t")]

        if len(rows) < 5:  # OCR returned nothing
            return []

        for row in rows:
            conf = float(row["conf"])

            if conf < 0:  # Is an outer box that surrounds inner boxes
                continue

            if not (text := row["text"].strip()):
                continue

            left = int(row["left"])
            top = int(row["top"])

            results.append(
                {
                    "conf": conf / 100.0,
                    "left": left,
                    "top": top,
                    "right": left + int(row["width"]) - 1,
                    "bottom": top + int(row["height"]) - 1,
                    "text": text,
                }
            )
    return results


def tesseract_dataframe(image: Image) -> list[dict]:
    """OCR the image with tesseract and return a data frame."""
    df = pytesseract.image_to_data(image, config=TESS_CONFIG, output_type="data.frame")

    df = df.loc[df.conf > 0]

    if df.shape[0] > 0:
        df.conf = df.conf / 100.0
        df.text = df.text.str.strip()
        df["right"] = df.left + df.width - 1
        df["bottom"] = df.top + df.height - 1
    else:
        df["right"] = None
        df["bottom"] = None

    df = df.loc[:, KEYS]
    return df


def easyocr_engine(image: Image) -> list[dict]:
    """OCR the image with easyOCR."""
    results = []
    image = np.asarray(image)
    raw = EASY_OCR.readtext(image, blocklist=CHAR_BLACKLIST)
    for item in raw:
        pos = item[0]
        results.append(
            {
                "conf": item[2],
                "left": int(pos[0][0]),
                "top": int(pos[0][1]),
                "right": int(pos[1][0]),
                "bottom": int(pos[2][1]),
                "text": item[1],
            }
        )
    return results
