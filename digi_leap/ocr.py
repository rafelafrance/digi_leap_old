"""OCR images."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import numpy.typing as npt
import pytesseract
from PIL import Image, ImageOps
from scipy import ndimage
from skimage import exposure as ex, filters, morphology as morph

import digi_leap.util as util
from digi_leap.ocr_score import OCRScore, score_tesseract, score_easyocr


class NoAdjustment(Exception):
    """Raise this if the adjustment is not needed."""
    pass


@dataclass
class ImageScore:
    """Hold image parameters."""
    image: npt.ArrayLike
    score: OCRScore


class AdjustImage:
    """Organize image adjustments using a variant of the strategy pattern."""

    def __init__(self, label: str = ''):
        self.label = label

    def __call__(self, best: ImageScore, scorers: dict[str, Callable]) -> ImageScore:
        """Adjust the image."""
        try:
            adjusted = self.adjust(best)
        except NoAdjustment:
            return best

        for engine, scorer in scorers.items():
            score_ = scorer(adjusted)
            if score_ > best.score:
                score_.carry_over(best.score, self.label, engine)
                best = ImageScore(adjusted, score_)

        self.after(best, adjusted)

        return best

    def adjust(self, best: ImageScore) -> Image:
        """Perform the image adjustment."""
        return best.image

    def after(self,  best: ImageScore, image: Image) -> None:
        """Actions for after the scoring."""


class Nothing(AdjustImage):
    """Just score the image without any adjustments."""

    def __init__(self, label='nothing'):
        super().__init__(label)


class Scale(AdjustImage):
    """Try a bigger label."""

    def __init__(self, label: str = '', factor: float = 2.0,  min_dim: int = 512):
        label = label if label else f'scaled by: {factor}'
        super().__init__(label)
        self.factor = factor
        self.min_dim = min_dim

    def adjust(self,  best: ImageScore) -> Image:
        """Perform the image adjustment."""
        image = util.to_pil(best.image)
        image = ImageOps.scale(image, self.factor)
        return image

    def after(self,  best: ImageScore, image: Image) -> ImageScore:
        """Actions for after the scoring."""
        if best.image.shape[0] < self.min_dim or best.image.shape[1] < self.min_dim:
            best.image = np.asarray(image)
            best.score.log(self.label)
        return best


class Rotate(AdjustImage):
    """Try adjusting the rotation of the image."""

    def __init__(self, label='rotated by:'):
        super().__init__(label)

    def adjust(self, best: ImageScore) -> Image:
        """Perform the image adjustment."""
        osd = pytesseract.image_to_osd(best.image)
        angle = int(re.search(r'degrees:\s*(\d+)', osd).group(1))

        if angle == 0:
            raise NoAdjustment

        self.label = f'rotated by: {angle}'
        data = np.asarray(best.image).copy()
        rotated = ndimage.rotate(data, angle, mode='nearest')
        return rotated


class Deskew(AdjustImage):
    """Try adjusting the rotation of the image."""

    def __init__(self, label='deskewed by:'):
        super().__init__(label)

    def adjust(self, best: ImageScore) -> Image:
        """Perform the image adjustment."""
        angle = util.find_skew(best.image)

        if angle == 0.0:
            raise NoAdjustment

        self.label = f'deskewed by: {angle}'
        data = np.asarray(best.image).copy()
        rotated = ndimage.rotate(data, angle, mode='nearest')
        return rotated


class RankModal(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, label: str = '', selem: npt.ArrayLike = None):
        label = label if label else 'rank modal: disk(2)'
        super().__init__(label)
        self.selem = selem if selem else morph.disk(2)

    def adjust(self, best: ImageScore) -> Image:
        """Perform the image adjustment."""
        ranked = filters.rank.modal(best.image.copy(), selem=self.selem)
        return ranked


class Exposure(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, label: str = '', gamma: float = 2.0):
        label = label if label else f'adjust exposure: gamma = {gamma}'
        super().__init__(label)
        self.gamma = gamma

    def adjust(self, best: ImageScore) -> Image:
        """Perform the image adjustment."""
        adjusted = ex.adjust_gamma(best.image, gamma=self.gamma)
        adjusted = ex.rescale_intensity(adjusted)
        return adjusted


class Binarize(AdjustImage):
    """Binarize the image."""

    def __init__(self, label: str = '', window_size: int = 11, k: float = 0.032):
        if not label:
            label = f'sauvola threshold: window size = {window_size} K = {k}'
        super().__init__(label)
        self.window_size = window_size
        self.k = k

    def adjust(self, best: ImageScore) -> Image:
        """Perform the image adjustment."""
        binary = np.asarray(best.image).copy()
        threshold = filters.threshold_sauvola(
            binary, window_size=self.window_size, k=self.k)
        binary = binary < threshold
        return binary


class RemoveSmallObjects(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, label: str = '', min_size: int = 64):
        label = label if label else f'removed small objects: min_size = {min_size}'
        super().__init__(label)
        self.min_size = min_size

    def adjust(self, best: ImageScore) -> Image:
        """Perform the image adjustment."""
        cleaned = morph.remove_small_objects(best.image, min_size=self.min_size)
        return cleaned


class BinaryOpening(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, label: str = '', selem: npt.ArrayLike = None):
        label = label if label else 'binary opening: selem=cross'
        super().__init__(label)
        self.selem = selem

    def adjust(self, best: ImageScore) -> Image:
        """Perform the image adjustment."""
        cleaned = morph.binary_opening(best.image, selem=self.selem)
        return cleaned


def ocr_label(path: Path) -> ImageScore:
    """Try to OCR the image.

    Adjust the image with greedy heuristics. Stop as soon as things are "good enough".
    """
    scorers = {'tesseract': score_tesseract, 'easyocr': score_easyocr}
    adjustments: list[Callable] = [
        Nothing(),
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
