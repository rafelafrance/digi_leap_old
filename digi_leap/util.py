"""Common utilities."""

import numpy as np
from PIL import Image
from numpy import typing as npt
from scipy.ndimage import interpolation as interp
from skimage.transform import probabilistic_hough_line

from digi_leap.const import HORIZ_ANGLES


def to_pil(label) -> Image:
    """Convert the label data into a PIL image"""
    # if hasattr(label, 'shape') and len(label.shape) == 3:
    #     label = label[:, :, 0]
    if hasattr(label, 'dtype') and label.dtype == 'float64':
        mode = 'L' if len(label.shape) < 3 else 'RGB'
        return Image.fromarray(label * 255.0, mode)
    if hasattr(label, 'dtype') and label.dtype == 'bool':
        image = (label * 255).astype('uint8')
        mode = 'L' if len(label.shape) < 3 else 'RGB'
        return Image.fromarray(image, mode)
    return Image.fromarray(label, 'L')


def to_opencv(image) -> Image:
    """Convert the image into a format opencv can handle."""
    image = np.asarray(image)
    if image.dtype == 'bool':
        return (image * 255).astype('uint8')
    return image


def find_skew(label: Image) -> float:
    """Find the skew of the label.

    This method is looking for sharp breaks between the characters and spaces.
    It will work best with binary images.
    """
    label = np.array(label).astype(np.int8)
    scores = []
    for angle in HORIZ_ANGLES:
        rotated = interp.rotate(label, angle, reshape=False, order=0)
        proj = np.sum(rotated, axis=1)
        score = np.sum((proj[1:] - proj[:-1]) ** 2)
        scores.append(score)
    best = max(scores)
    best = HORIZ_ANGLES[scores.index(best)]
    return best


def find_lines(label: npt.ArrayLike, thetas, line_length=50, line_gap=6) -> list[tuple]:
    """Find lines on the label using the Hough Transform."""
    lines = probabilistic_hough_line(
        label,
        theta=thetas,
        line_length=line_length,
        line_gap=line_gap)
    return lines
