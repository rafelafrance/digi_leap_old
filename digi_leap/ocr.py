"""OCR images."""

from dataclasses import dataclass
from typing import Callable

from PIL import Image

from digi_leap.label_transforms import (
    Binarize,
    BinaryOpening,
    BinaryRemoveSmallHoles,
    BinaryThin,
    Deskew,
    LabelTransform,
    RankMean,
    Rotate,
    Scale,
)
from digi_leap.ocr_score import OCRScore, score_easyocr, score_tesseract

SCORERS = {"tesseract": score_tesseract, "easyocr": score_easyocr}
TRANSFORMS: list[Callable] = [
    Scale(),
    Rotate(),
    Deskew(),
    RankMean(),
    Binarize(),
    BinaryRemoveSmallHoles(area_threshold=24),
    BinaryThin(max_iter=2),
    BinaryOpening(),
]


@dataclass
class ImageScore:
    """Hold image parameters."""

    image: Image
    score: OCRScore


def ocr_label(image: Image) -> ImageScore:
    """Try to OCR the image."""
    image = LabelTransform.as_array(image)

    for transform in TRANSFORMS:
        image = transform(image)

    image = LabelTransform.to_pil(image)

    best = OCRScore(total=-1)
    for key, scorer in SCORERS.items():
        score = scorer(image)
        if score > best:
            best = score

    return ImageScore(image, best)
