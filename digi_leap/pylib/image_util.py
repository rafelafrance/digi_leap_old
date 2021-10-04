"""Manipulate images to help with the OCR process."""

import numpy as np
from numpy import typing as npt
from PIL import Image


def profile_projection(image: Image, axis: int = 1) -> npt.ArrayLike:
    """Get a profile projection of a binary image."""
    array = np.asarray(image).copy()

    array[array == 0] = 1
    array[array == 255] = 0

    proj = np.sum(array, axis=axis)
    return proj
