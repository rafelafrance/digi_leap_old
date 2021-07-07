"""Image transforms performed on labels before OCR."""

import re
from abc import ABC, abstractmethod
from typing import Callable

import numpy as np
import pytesseract
from numpy import typing as npt
from PIL import Image
from scipy import ndimage
from skimage import exposure as ex
from skimage import filters
from skimage import morphology as morph
from skimage import util as sk_util

from digi_leap import util as util


# TODO: Cleanly handle gray scale vs binary images in the chain of transformations
class LabelTransform(ABC):
    """Base class for image transforms for labels."""

    @abstractmethod
    def __call__(self, image: Image) -> npt.ArrayLike:
        """Perform a transformation of the label image."""

    @staticmethod
    def as_array(image: Image) -> npt.ArrayLike:
        """Convert a PIL image to a gray scale numpy array."""
        image = image.convert("L")
        return np.asarray(image).copy()

    @staticmethod
    def to_pil(image: npt.ArrayLike) -> Image:
        """Convert a numpy array to a PIL image."""
        return util.to_pil(image)


class Scale(LabelTransform):
    """Enlarge an image if it is too small."""

    def __init__(self, factor: float = 2.0, min_dim: int = 512):
        self.factor = factor
        self.min_dim = min_dim

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        if image.shape[0] < self.min_dim or image.shape[1] < self.min_dim:
            image = ndimage.zoom(image, self.factor)
        return image


class Rotate(LabelTransform):
    """Adjust the orientation of the image."""

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        osd = pytesseract.image_to_osd(image)
        angle = int(re.search(r"degrees:\s*(\d+)", osd).group(1))

        if angle != 0:
            image = ndimage.rotate(image, angle, mode="nearest")

        return image


class Deskew(LabelTransform):
    """Tweak the rotation of the image."""

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        """Perform the image transform."""
        angle = util.find_skew(image)

        if angle != 0.0:
            image = ndimage.rotate(image, angle, mode="nearest")

        return image


class RankMean(LabelTransform):
    """Filter the image using a mean filter."""

    def __init__(self, selem2d: npt.ArrayLike = None, selem3d: npt.ArrayLike = None):
        self.selem2d = selem2d if selem2d else morph.disk(2)
        self.selem3d = selem3d if selem3d else morph.ball(3)

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        selem = self.selem2d if len(image.shape) == 2 else self.selem3d
        image = filters.rank.mean(image, selem=selem)
        return image


class RankMedian(LabelTransform):
    """Filter the image using a mean filter."""

    def __init__(self, selem2d: npt.ArrayLike = None, selem3d: npt.ArrayLike = None):
        self.selem2d = selem2d if selem2d else morph.disk(2)
        self.selem3d = selem3d if selem3d else morph.ball(3)

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        selem = self.selem2d if len(image.shape) == 2 else self.selem3d
        image = filters.rank.median(image, selem=selem)
        return image


class RankModal(LabelTransform):
    """Filter the image using a modal filter."""

    def __init__(self, selem2d: npt.ArrayLike = None, selem3d: npt.ArrayLike = None):
        self.selem2d = selem2d if selem2d else morph.disk(2)
        self.selem3d = selem3d if selem3d else morph.ball(3)

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        selem = self.selem2d if len(image.shape) == 2 else self.selem3d
        image = filters.rank.modal(image, selem=selem)
        return image


class Blur(LabelTransform):
    """Blur the image."""

    def __init__(self, sigma: int = 1):
        self.sigma = sigma

    def __call__(self, image: npt.ArrayLike, sigma: int = None) -> npt.ArrayLike:
        sigma = sigma if sigma else self.sigma
        multichannel = len(image.shape) > 2
        image = filters.gaussian(image, sigma=sigma, multichannel=multichannel)
        return image


class Exposure(LabelTransform):
    """Stretching or shrinking an image's intensity levels."""

    def __init__(self, gamma: float = 2.0):
        self.gamma = gamma

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        image = ex.adjust_gamma(image, gamma=self.gamma)
        image = ex.rescale_intensity(image)
        return image


class BinarizeSauvola(LabelTransform):
    """Binarize the image."""

    def __init__(self, window_size: int = 11, k: float = 0.032):
        self.window_size = window_size
        self.k = k

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        threshold = filters.threshold_sauvola(
            image, window_size=self.window_size, k=self.k
        )
        image = image > threshold
        return image


class BinaryRemoveSmallHoles(LabelTransform):
    """Remove contiguous holes smaller than the specified size in a binary image."""

    def __init__(self, area_threshold: int = 64):
        self.area_threshold = area_threshold

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        image = morph.remove_small_holes(image, area_threshold=self.area_threshold)
        return image


class BinaryOpening(LabelTransform):
    """Fast binary morphological opening of a binary image."""

    def __init__(self, selem: npt.ArrayLike = None):
        self.selem = selem

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        image = morph.binary_opening(image, selem=self.selem)
        return image


class BinaryThin(LabelTransform):
    """Perform morphological thinning of a binary image."""

    def __init__(self, max_iter: int = None):
        self.max_iter = max_iter

    def __call__(self, image: npt.ArrayLike) -> npt.ArrayLike:
        image = sk_util.invert(image)
        image = morph.thin(image, max_iter=self.max_iter)
        image = sk_util.invert(image)
        return image


TRANSFORMS: list[Callable] = [
    Scale(),
    Rotate(),
    Deskew(),
    RankMedian(),
    BinarizeSauvola(),
    BinaryRemoveSmallHoles(area_threshold=24),
    BinaryThin(max_iter=2),
    BinaryOpening(),
]


def transform_label(image: Image) -> Image:
    """Try to OCR the image."""
    image = LabelTransform.as_array(image)

    for transform in TRANSFORMS:
        image = transform(image)

    image = LabelTransform.to_pil(image)
    return image
