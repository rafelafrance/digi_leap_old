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


# TODO: Cleanly handle gray scale vs binary images in transformation pipeline


class LabelTransform(ABC):
    """Base class for image transforms for labels."""

    @abstractmethod
    def __call__(self, image: Image) -> tuple[npt.ArrayLike, str]:
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

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        if image.shape[0] < self.min_dim or image.shape[1] < self.min_dim:
            image = ndimage.zoom(image, self.factor)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.factor=}, {self.min_dim=})"


class Rotate(LabelTransform):
    """Adjust the orientation of the image."""

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        osd = pytesseract.image_to_osd(image)
        angle = int(re.search(r"degrees:\s*(\d+)", osd).group(1))

        if angle != 0:
            image = ndimage.rotate(image, angle, mode="nearest")

        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}(pytesseract.image_to_osd, mode='nearest')"


class Deskew(LabelTransform):
    """Tweak the rotation of the image."""

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        """Perform the image transform."""
        angle = util.find_skew(image)

        if angle != 0.0:
            image = ndimage.rotate(image, angle, mode="nearest")

        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}(util.find_skew, mode='nearest')"


class RankMean(LabelTransform):
    """Filter the image using a mean filter."""

    def __init__(self, selem: npt.ArrayLike = None):
        self.selem = selem if selem else morph.disk(2)

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = filters.rank.mean(image, selem=self.selem)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        selem = str(self.selem).replace("\n", ",")
        return f"{name}({selem=})"


class RankMedian(LabelTransform):
    """Filter the image using a mean filter."""

    def __init__(self, selem: npt.ArrayLike = None):
        self.selem = selem if selem else morph.disk(2)

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = filters.rank.median(image, selem=self.selem)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        selem = str(self.selem).replace("\n", ",")
        return f"{name}({selem=})"


class RankModal(LabelTransform):
    """Filter the image using a modal filter."""

    def __init__(self, selem: npt.ArrayLike = None):
        self.selem = selem if selem else morph.disk(2)

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = filters.rank.median(image, selem=self.selem)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        selem = str(self.selem).replace("\n", ",")
        return f"{name}({selem=})"


class Blur(LabelTransform):
    """Blur the image."""

    def __init__(self, sigma: int = 1):
        self.sigma = sigma

    def __call__(
        self, image: npt.ArrayLike, sigma: int = None
    ) -> tuple[npt.ArrayLike, str]:
        sigma = sigma if sigma else self.sigma
        multichannel = len(image.shape) > 2
        image = filters.gaussian(image, sigma=sigma, multichannel=multichannel)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.sigma=})"


class Exposure(LabelTransform):
    """Stretching or shrinking an image's intensity levels."""

    def __init__(self, gamma: float = 2.0):
        self.gamma = gamma

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = ex.adjust_gamma(image, gamma=self.gamma)
        image = ex.rescale_intensity(image)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.gamma=})"


class BinarizeSauvola(LabelTransform):
    """Binarize the image."""

    def __init__(self, window_size: int = 11, k: float = 0.032):
        self.window_size = window_size
        self.k = k

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        threshold = filters.threshold_sauvola(
            image, window_size=self.window_size, k=self.k
        )
        image = image > threshold
        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.window_size=}, {self.k=})"


class BinaryRemoveSmallHoles(LabelTransform):
    """Remove contiguous holes smaller than the specified size in a binary image."""

    def __init__(self, area_threshold: int = 64):
        self.area_threshold = area_threshold

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = morph.remove_small_holes(image, area_threshold=self.area_threshold)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.area_threshold=})"


class BinaryOpening(LabelTransform):
    """Fast binary morphological opening of a binary image."""

    def __init__(self, selem: npt.ArrayLike = None):
        self.selem = selem

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = morph.binary_opening(image, selem=self.selem)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.selem=})"


class BinaryThin(LabelTransform):
    """Perform morphological thinning of a binary image."""

    def __init__(self, max_iter: int = None):
        self.max_iter = max_iter

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = sk_util.invert(image)
        image = morph.thin(image, max_iter=self.max_iter)
        image = sk_util.invert(image)
        return image

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.max_iter=})"


# A default label transform pipeline
DEFAULT_PIPELINE: list[Callable] = [
    Scale(),
    Rotate(),
    Deskew(),
    RankMedian(),
    BinarizeSauvola(),
    BinaryRemoveSmallHoles(area_threshold=24),
    BinaryThin(max_iter=2),
    BinaryOpening(),
]


def transform_label(transforms: list[Callable], image: Image) -> Image:
    """Transform the label to improve OCR results."""
    image = LabelTransform.as_array(image)

    actions = []
    for func in transforms:
        image, action = func(image)
        actions.append(action)

    image = LabelTransform.to_pil(image)
    return image, actions
