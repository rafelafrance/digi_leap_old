"""OCR images."""
import easyocr
import numpy as np
import pytesseract

ENGINES = ["easyocr", "tesseract"]


class EngineConfig:

    easy_ocr = easyocr.Reader(["en"], gpu=True)

    char_blacklist = "¥€£¢$«»®©™§{}[]<>|~"
    tess_lang = "eng"
    tess_config = " ".join(
        [
            f"-l {tess_lang}",
            f"-c tessedit_char_blacklist='{char_blacklist}'",
        ]
    )


def tesseract_engine(image) -> list[dict]:
    df = pytesseract.image_to_data(
        image, config=EngineConfig.tess_config, output_type="data.frame"
    )

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

    df = df.loc[:, ["conf", "left", "top", "right", "bottom", "text"]]

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
    results = []
    image = np.asarray(image)
    raw = EngineConfig.easy_ocr.readtext(image, blocklist=EngineConfig.char_blacklist)
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


def easy_text(image):
    """Return text without other information."""
    image = np.asarray(image)
    text = EngineConfig.easy_ocr.readtext(
        image, blocklist=EngineConfig.char_blacklist, detail=0
    )
    text = " ".join(text)
    return text


def tess_text(image):
    """Return text without other information."""
    text = pytesseract.image_to_string(image, config=EngineConfig.tess_config)
    return text
