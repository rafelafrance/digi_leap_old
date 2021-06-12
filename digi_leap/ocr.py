"""OCR images."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt
import pytesseract
from PIL import Image, ImageOps
from scipy import ndimage
from skimage import exposure as ex, filters, morphology as morph

import digi_leap.util as util
from digi_leap.ocr_score import OCRScore, score_tesseract, score_easyocr


@dataclass
class ImageScore:
    """Hold image parameters."""
    image: npt.ArrayLike
    score: OCRScore


class AdjustImage(ABC):
    """Organize image adjustments using a variant of the strategy pattern."""

    @abstractmethod
    def __call__(self, image: Image) -> Image:
        """Adjust the image."""


class Scale(AdjustImage):
    """Try a bigger label."""

    def __init__(self, factor: float = 2.0,  min_dim: int = 512):
        self.factor = factor
        self.min_dim = min_dim

    def __call__(self,  image: Image) -> Image:
        """Perform the image adjustment."""
        if image.shape[0] < self.min_dim or image.shape[1] < self.min_dim:
            image = ImageOps.scale(image, self.factor)
        return image


class Rotate(AdjustImage):
    """Try adjusting the rotation of the image."""

    def __call__(self, image: Image) -> Image:
        """Perform the image adjustment."""
        osd = pytesseract.image_to_osd(image)
        angle = int(re.search(r'degrees:\s*(\d+)', osd).group(1))

        if angle != 0:
            image = np.asarray(image).copy()
            image = ndimage.rotate(image, angle, mode='nearest')

        return util.to_pil(image)


class Deskew(AdjustImage):
    """Try adjusting the rotation of the image."""

    def __call__(self, image: Image) -> Image:
        """Perform the image adjustment."""
        angle = util.find_skew(image)

        if angle == 0.0:
            self.label = f'deskewed by: {angle}'
            image = np.asarray(image).copy()
            image = ndimage.rotate(image, angle, mode='nearest')

        return util.to_pil(image)


class RankModal(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, selem: npt.ArrayLike = None):
        self.selem = selem if selem else morph.disk(2)

    def __call__(self, image: Image) -> Image:
        """Perform the image adjustment."""
        image = filters.rank.modal(image.copy(), selem=self.selem)
        return util.to_pil(image)


class Exposure(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, gamma: float = 2.0):
        self.gamma = gamma

    def __call__(self, image: Image) -> Image:
        """Perform the image adjustment."""
        image = ex.adjust_gamma(image, gamma=self.gamma)
        image = ex.rescale_intensity(image)
        return util.to_pil(image)


class Binarize(AdjustImage):
    """Binarize the image."""

    def __init__(self, window_size: int = 11, k: float = 0.032):
        self.window_size = window_size
        self.k = k

    def __call__(self, image: Image) -> Image:
        """Perform the image adjustment."""
        image = np.asarray(image).copy()
        threshold = filters.threshold_sauvola(
            image, window_size=self.window_size, k=self.k)
        image = image < threshold
        return util.to_pil(image)


class RemoveSmallObjects(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, min_size: int = 64):
        self.min_size = min_size

    def __call__(self, image: Image) -> Image:
        """Perform the image adjustment."""
        image = np.asarray(image).copy()
        image = morph.remove_small_objects(image, min_size=self.min_size)
        return util.to_pil(image)


class BinaryOpening(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, label: str = '', selem: npt.ArrayLike = None):
        label = label if label else 'binary opening: selem=cross'
        super().__init__(label)
        self.selem = selem

    def __call__(self, image: Image) -> Image:
        """Perform the image adjustment."""
        image = morph.binary_opening(image, selem=self.selem)
        return image


def ocr_label(path: Path) -> ImageScore:
    """Try to OCR the image.

    Adjust the image with greedy heuristics. Stop as soon as things are "good enough".
    """
    scorers = {'tesseract': score_tesseract, 'easyocr': score_easyocr}
    adjustments: list[Callable] = [
        Scale(),
        Rotate(),
        Deskew(),
        RankModal(),
        Exposure(),
        Binarize(),
        RemoveSmallObjects(),
        BinaryOpening(),
    ]

    image = Image.open(path).convert('L').copy()
    score = OCRScore(found=-1)
    best = ImageScore(np.asarray(image), score)

    for adjustment in adjustments:
        best = adjustment(best, scorers)
        if best.score.is_ok:
            return best

    return best
