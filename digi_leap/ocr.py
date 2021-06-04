"""OCR images."""

import re
from abc import ABC, abstractmethod
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
from digi_leap.ocr_score import OCRScore, score_tesseract


@dataclass
class ImageScore:
    """Hold image parameters."""
    image: npt.ArrayLike
    score: OCRScore


class AdjustImage(ABC):
    """Organize image adjustments using a variant of the strategy pattern."""

    def __init__(self, scorer: Callable, label: str = ''):
        self.scorer = scorer
        self.label = label

    @abstractmethod
    def __call__(self, best: ImageScore) -> ImageScore:
        """Adjust the image."""
        pass

    def score(self, best: ImageScore, adjusted: Image) -> ImageScore:
        """Score the OCR results and handle a better score."""
        image = util.to_pil(adjusted)
        score_ = self.scorer(image)
        if score_ > best.score:
            method = best.score.method
            best = ImageScore(adjusted, score_)
            best.score.method = method
            best.score.log(self.label)
        return best


class Nothing(AdjustImage):
    """Just score the image without any adjustments."""

    def __init__(self, scorer: Callable, label='nothing'):
        super().__init__(scorer, label)

    def __call__(self, best: ImageScore) -> ImageScore:
        return self.score(best, best.image)


class Scale(AdjustImage):
    """Try a bigger label."""

    def __init__(
            self, scorer: Callable,
            label: str = '',
            factor: float = 2.0,
            min_dim: int = 512,
    ):
        label = label if label else f'scaled by: {factor}'
        super().__init__(scorer, label)
        self.factor = factor
        self.min_dim = min_dim

    def __call__(self, best: ImageScore) -> ImageScore:
        bigger = util.to_pil(best.image)
        bigger = ImageOps.scale(bigger, self.factor)
        best = self.score(best, np.asarray(bigger))
        if best.image.shape[0] < self.min_dim or best.image.shape[1] < self.min_dim:
            best.image = np.asarray(bigger)
            best.score.log(self.label)
        return best


class Rotate(AdjustImage):
    """Try adjusting the rotation of the image."""

    def __init__(self, scorer: Callable, label='rotated by:'):
        super().__init__(scorer, label)

    def __call__(self, best: ImageScore) -> ImageScore:
        osd = pytesseract.image_to_osd(best.image)
        angle = int(re.search(r'degrees:\s*(\d+)', osd).group(1))
        if angle != 0:
            self.label = f'rotated by: {angle}'
            data = np.asarray(best.image).copy()
            rotated = ndimage.rotate(data, angle, mode='nearest')
            best = self.score(best, rotated)
        return best


class Deskew(AdjustImage):
    """Try adjusting the rotation of the image."""

    def __init__(self, scorer: Callable, label='deskewed by:'):
        super().__init__(scorer, label)

    def __call__(self, best: ImageScore) -> ImageScore:
        angle = util.find_skew(best.image)
        if angle != 0.0:
            print(angle)
            self.label = f'deskewed by: {angle}'
            data = np.asarray(best.image).copy()
            rotated = ndimage.rotate(data, angle, mode='nearest')
            best = self.score(best, rotated)
        return best


class RankModal(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, scorer: Callable, label: str = '', selem: npt.ArrayLike = None):
        label = label if label else 'rank modal: disk(2)'
        super().__init__(scorer, label)
        self.selem = selem if selem else morph.disk(2)

    def __call__(self, best: ImageScore) -> ImageScore:
        ranked = filters.rank.modal(best.image.copy(), selem=self.selem)
        best = self.score(best, ranked)
        return best


class Exposure(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, scorer: Callable, label: str = '', gamma: float = 2.0):
        label = label if label else f'adjust exposure: gamma = {gamma}'
        super().__init__(scorer, label)
        self.gamma = gamma

    def __call__(self, best: ImageScore) -> ImageScore:
        adjusted = ex.adjust_gamma(best.image, gamma=self.gamma)
        adjusted = ex.rescale_intensity(adjusted)
        best = self.score(best, adjusted)
        return best


class Binarize(AdjustImage):
    """Binarize the image."""

    def __init__(
            self,
            scorer: Callable,
            label: str = '',
            window_size: int = 11,
            k: float = 0.032,
    ):
        if not label:
            label = f'sauvola threshold: window size = {window_size} K = {k}'
        super().__init__(scorer, label)
        self.window_size = window_size
        self.k = k

    def __call__(self, best: ImageScore) -> ImageScore:
        binary = np.asarray(best.image).copy()
        threshold = filters.threshold_sauvola(
            binary, window_size=self.window_size, k=self.k)
        binary = binary < threshold
        best = self.score(best, binary)
        return best


class RemoveSmallObjects(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, scorer: Callable, label: str = '', min_size: int = 64):
        label = label if label else f'removed small objects: min_size = {min_size}'
        super().__init__(scorer, label)
        self.min_size = min_size

    def __call__(self, best: ImageScore) -> ImageScore:
        cleaned = morph.remove_small_objects(best.image, min_size=self.min_size)
        best = self.score(best, cleaned)
        return best


class BinaryOpening(AdjustImage):
    """Filter the image using a modal filter."""

    def __init__(self, scorer: Callable, label: str = '', selem: npt.ArrayLike = None):
        label = label if label else 'binary opening: selem=cross'
        super().__init__(scorer, label)
        self.selem = selem

    def __call__(self, best: ImageScore) -> ImageScore:
        cleaned = morph.binary_opening(best.image, selem=self.selem)
        best = self.score(best, cleaned)
        return best


def ocr_label(path: Path, scorer=score_tesseract) -> ImageScore:
    """Try to OCR the image.

    Adjust the image with greedy heuristics. Stop as soon as things are "good enough".
    """
    adjustments = [
        Nothing(scorer),
        Scale(scorer),
        Rotate(scorer),
        Deskew(scorer),
        RankModal(scorer),
        Exposure(scorer),
        Binarize(scorer),
        RemoveSmallObjects(scorer),
        BinaryOpening(scorer),
    ]

    image = Image.open(path).convert('L').copy()
    score = OCRScore(found=-1)
    best = ImageScore(np.asarray(image), score)

    for adjust in adjustments:
        best = adjust(best)
        if best.score.is_ok:
            return best

    return best
