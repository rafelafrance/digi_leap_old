"""OCR images."""
import easyocr
import numpy as np
import pytesseract

EASY_OCR = easyocr.Reader(["en"])

KEYS = """conf left top right bottom text""".split()

CHAR_BLACKLIST = "¥€£¢$«»®©™§{}[]<>|"
TESS_LANG = "eng"
TESS_CONFIG = " ".join(
    [
        f"-l {TESS_LANG}",
        f"-c tessedit_char_blacklist='{CHAR_BLACKLIST}'",
    ]
)


def tesseract_engine(image) -> list[dict]:
    """OCR the image with tesseract."""
    df = pytesseract.image_to_data(image, config=TESS_CONFIG, output_type="data.frame")

    df = df.loc[df.conf > 0]

    if df.shape[0] > 0:
        df.text = df.text.astype(str)
        df.text = df.text.str.strip()
        df.conf /= 100.0
        df["right"] = df.left + df.width
        df["bottom"] = df.top + df.height
    else:
        df["right"] = None
        df["bottom"] = None

    df = df.loc[:, KEYS]

    df = df.rename(
        columns={
            "left": "ocr_left",
            "top": "ocr_top",
            "right": "ocr_right",
            "bottom": "ocr_bottom",
            "text": "ocr_text",
        }
    )

    results = df.to_dict("records")
    return results


def easyocr_engine(image) -> list[dict]:
    """OCR the image with easyOCR."""
    results = []
    image = np.asarray(image)
    raw = EASY_OCR.readtext(image, blocklist=CHAR_BLACKLIST)
    for item in raw:
        pos = item[0]
        results.append(
            {
                "conf": item[2],
                "ocr_left": int(pos[0][0]),
                "ocr_top": int(pos[0][1]),
                "ocr_right": int(pos[1][0]),
                "ocr_bottom": int(pos[2][1]),
                "ocr_text": item[1],
            }
        )
    return results
