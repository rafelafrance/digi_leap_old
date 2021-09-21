"""OCR images."""

import easyocr
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image

EASY_OCR = easyocr.Reader(["en"])

KEYS = """conf left top right bottom text""".split()

CHAR_BLACKLIST = "¥€£¢$«»®©§{}[]<>|"
TESS_LANG = "eng"
TESS_CONFIG = " ".join(
    [
        f"-l {TESS_LANG}",
        f"-c tessedit_char_blacklist='{CHAR_BLACKLIST}'",
    ]
)


def tesseract_dataframe(image: Image) -> pd.DataFrame:
    """OCR the image with tesseract and return a data frame."""
    df = pytesseract.image_to_data(image, config=TESS_CONFIG, output_type="data.frame")

    df = df.loc[df.conf > 0]

    if df.shape[0] > 0:
        df.text = df.text.astype(str)
        df.text = df.text.str.strip()
        df.conf /= 100.0
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
