"""Image transforms performed on labels before OCR."""

import re
from abc import ABC, abstractmethod
from typing import Callable

import numpy as np
import pytesseract
from PIL import Image
from numpy import typing as npt
from pytesseract.pytesseract import TesseractError
from scipy import ndimage
from scipy.ndimage import interpolation as interp
from skimage import exposure as ex, filters, morphology as morph, util as sk_util


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
        return np.asarray(image)

    # TODO: This method is a mess
    @staticmethod
    def to_pil(image: npt.ArrayLike) -> Image:
        """Convert a numpy array to a PIL image."""
        if hasattr(image, "dtype") and image.dtype == "float64":
            mode = "L" if len(image.shape) < 3 else "RGB"
            return Image.fromarray(image * 255.0, mode)
        if hasattr(image, "dtype") and image.dtype == "bool":
            image = (image * 255).astype("uint8")
            mode = "L" if len(image.shape) < 3 else "RGB"
            return Image.fromarray(image, mode)
        return Image.fromarray(image, "L")


class Scale(LabelTransform):
    """Enlarge an image if it is too small."""

    def __init__(self, factor: float = 2.0, min_dim: int = 512, mode: str = "constant"):
        self.factor = factor
        self.min_dim = min_dim
        self.mode = mode

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        action = repr(self)
        if image.shape[0] < self.min_dim or image.shape[1] < self.min_dim:
            image = ndimage.zoom(image, self.factor, mode=self.mode)
        else:
            action += " skipped"
        return image, action

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.factor=}, {self.min_dim=}, {self.mode=})"


class Blur(LabelTransform):
    """Blur the image."""

    def __init__(self, sigma: float = 1.0):
        self.sigma = sigma

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = ndimage.gaussian_filter(image, self.sigma)
        return image, repr(self)

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.sigma=})"


class Orient(LabelTransform):
    """Adjust the orientation of the image."""

    def __init__(self, conf_low: float = 15.0, conf_high: float = 100.0):
        self.conf_low = conf_low
        self.conf_high = conf_high

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        action = repr(self)

        try:
            osd = pytesseract.image_to_osd(image)
        except TesseractError:
            action += " skipped"
            return image, action

        angle = 0
        if match := re.search(r"Rotate: (\d+)", osd):
            angle = int(match.group(1))

        conf = 0.0
        if match := re.search(r"Orientation confidence: ([\d.]+)", osd):
            conf = float(match.group(1))

        if angle != 0 and self.conf_low <= conf <= self.conf_high:
            image = ndimage.rotate(image, angle, mode="nearest")
        else:
            action += " skipped"

        return image, action

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}(pytesseract.image_to_osd, mode='nearest')"


class Deskew(LabelTransform):
    """Tweak the rotation of the image."""

    # TODO: More angles
    horiz_angles = np.array([0.0, 0.5, -0.5, 1.0, -1.0, 1.5, -1.5, 2.0, -2.0])

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        """Perform the image transform."""
        action = repr(self)
        angle = self.find_skew(image)

        if angle != 0.0:
            image = ndimage.rotate(image, angle, mode="nearest")
        else:
            action += " skipped"

        return image, action

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}(util.find_skew, mode='nearest')"

    def find_skew(self, label: Image) -> float:
        """Find the skew of the label.

        This method is looking for sharp breaks between the characters and spaces.
        It will work best with binary images.
        """
        label = np.array(label).astype(np.int8)
        scores = []
        for angle in self.horiz_angles:
            rotated = interp.rotate(label, angle, reshape=False, order=0)
            proj = np.sum(rotated, axis=1)
            score = np.sum((proj[1:] - proj[:-1]) ** 2)
            scores.append(score)
        best = max(scores)
        best = self.horiz_angles[scores.index(best)]
        return best


class RankMean(LabelTransform):
    """Filter the image using a mean filter."""

    def __init__(self, selem: npt.ArrayLike = None):
        self.selem = selem if selem else morph.disk(2)

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = filters.rank.mean(image, selem=self.selem)
        return image, repr(self)

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
        return image, repr(self)

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
        return image, repr(self)

    def __repr__(self):
        name = self.__class__.__name__
        selem = str(self.selem).replace("\n", ",")
        return f"{name}({selem=})"


class EqualizeHist(LabelTransform):
    """Return image after histogram equalization."""

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = ex.equalize_hist(image)
        image = (image * 255).astype(np.int8)
        # footprint = morph.disk(30)
        # image = filters.rank.equalize(image, footprint)
        return image, repr(self)

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}()"


class Exposure(LabelTransform):
    """Stretching or shrinking an image's intensity levels."""

    def __init__(self, gamma: float = 2.0):
        self.gamma = gamma

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = ex.adjust_gamma(image, gamma=self.gamma)
        image = ex.rescale_intensity(image)
        return image, repr(self)

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
        return image, repr(self)

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.window_size=}, {self.k=})"


class BinaryRemoveSmallHoles(LabelTransform):
    """Remove contiguous holes smaller than the specified size in a binary image."""

    def __init__(self, area_threshold: int = 64, connectivity: int = 1):
        self.area_threshold = area_threshold
        self.connectivity = connectivity

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = morph.remove_small_holes(
            image, area_threshold=self.area_threshold, connectivity=self.connectivity
        )
        return image, repr(self)

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.area_threshold=})"


class BinaryOpening(LabelTransform):
    """Fast binary morphological opening of a binary image."""

    def __init__(self, selem: npt.ArrayLike = None):
        self.selem = selem

    def __call__(self, image: npt.ArrayLike) -> tuple[npt.ArrayLike, str]:
        image = morph.binary_opening(image, selem=self.selem)
        return image, repr(self)

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
        return image, repr(self)

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self.max_iter=})"


# =============================================================================
# Canned scripts for transforming labels

# If you plan to use an ensemble every ensemble pipeline must include the same
# affine transforms that modify the geometry of the image [Scale, Orient, Deskew].
# Else wise, it becomes almost impossible to align bounding boxes of each
# ensemble member. In the PIPELINES below you must use the same:
# Scale(mode="nearest"), Orient(), Deskew() in every ensemble member but you
# could exclude Blur() because that does not modify the image geometry.
BASE_PIPELINE: list[LabelTransform] = [
    Blur(sigma=0.5),
    Scale(mode="nearest"),
    Orient(),
    Deskew(),
]

PIPELINES: dict[str, list[LabelTransform]] = {
    "deskew": BASE_PIPELINE,
    "binarize": BASE_PIPELINE + [BinarizeSauvola()],
}


# =============================================================================
# Functions for applying transforms to images


def transform_label(pipeline: str, image: Image) -> Image:
    """Transform the label to improve OCR results."""
    return transform_image(PIPELINES[pipeline], image)


def transform_image(pipeline: list[Callable], image: Image) -> Image:
    """Transform the label to improve OCR results."""
    image = LabelTransform.as_array(image)

    actions = []
    for func in pipeline:
        image, action = func(image)
        actions.append(action)

    image = LabelTransform.to_pil(image)
    return image
