"""Functions for dealing with label images."""

from collections import namedtuple

import numpy as np
import numpy.typing as npt
from PIL import Image
from scipy.ndimage import interpolation as inter
from skimage import draw, filters
from skimage.transform import probabilistic_hough_line

Pair = namedtuple('Pair', 'start end')

# TODO: DO not use hardcoded parameters like these constants

PADDING = 2  # How many pixels to pad a line or word
INSIDE_ROW = 2  # Only merge rows if they are this close
OUTSIDE_ROW = 100  # Only merge rows if they do not make a row this fat

TESS_CONFIG = ' '.join([
    '-l eng',
    "-c tessedit_char_blacklist='€«¢»£®§{}©|'",
])

# In the order we want to scan
HORIZ_ANGLES = np.array([0.0, 0.5, -0.5, 1.0, -1.0, 1.5, -1.5, 2.0, -2.0])
NEAR_HORIZ = np.deg2rad(HORIZ_ANGLES)
NEAR_VERT = np.deg2rad(np.linspace(88.0, 92.0, num=9))
NEAR_HORIZ, NEAR_VERT = NEAR_VERT, NEAR_HORIZ  # ?!

ON, OFF = 255, 0


def find_skew(label: Image) -> float:
    """Find the skew of the label.

    This method is looking for sharp edges between the characters and spaces.
    It will work best with binary images.
    """
    label = np.array(label).astype(np.int8)
    scores = []
    for angle in HORIZ_ANGLES:
        rotated = inter.rotate(label, angle, reshape=False, order=0)
        proj = np.sum(rotated, axis=1)
        score = np.sum((proj[1:] - proj[:-1]) ** 2)
        scores.append(score)
    best = max(scores)
    best = HORIZ_ANGLES[scores.index(best)]
    return best


def to_pil(label: npt.ArrayLike) -> Image:
    """Convert the label into a PIL image"""
    if len(label.shape) == 3:
        label = label[:, :, 0]
    if label.dtype == 'float64':
        return Image.fromarray(label * 255.0).convert('L')
    return Image.fromarray(label)


# TODO: Calculate: window_size, k
def binarize(
        label: Image,
        window_size: int = 11,
        k: float = 0.032,
) -> np.ndarray:
    """Convert the label into a binary threshold form."""
    data: np.ndarray = np.asarray(label).copy()
    threshold = filters.threshold_sauvola(data, window_size=window_size, k=k)
    data = data < threshold
    return data


# TODO: Calculate: line_length, line_gap
def find_lines(label: npt.ArrayLike, thetas, line_length=50, line_gap=6) -> list[tuple]:
    """Find lines on the label using the Hough Transform."""
    lines = probabilistic_hough_line(
        label,
        theta=thetas,
        line_length=line_length,
        line_gap=line_gap)
    return lines


# TODO: Calculate: line_width, window, threshold
def remove_horiz_lines(
        label: npt.ArrayLike, lines, line_width=6, window=8, threshold=1
):
    """Remove horizontal lines from the label."""
    rad, win = line_width // 2, window // 2
    for line in lines:
        (c0, r0), (c1, r1) = line
        rows, cols = draw.line(r0, c0, r1, c1)

        for row, col in zip(rows, cols):
            inside = label[row - rad:row + rad, col].sum()
            outside = label[row - win:row + win, col].sum()
            if inside != 0 and (outside - inside) < threshold:
                label[row - rad:row + rad, col] = False


# TODO: Calculate: line_width, window, threshold
def remove_vert_lines(
        label: npt.ArrayLike, lines, line_width=6, window=10, threshold=6
):
    """Remove vertical lines from the label."""
    rad, win = line_width // 2, window // 2
    for line in lines:
        (c0, r0), (c1, r1) = line
        rows, cols = draw.line(r0, c0, r1, c1)

        for row, col in zip(rows, cols):
            outside = label[row, col - win:col + win].sum()
            inside = label[row, col - rad:col + rad].sum()
            if inside != 0 and (outside - inside) < threshold:
                label[row, col - rad:col + rad] = False


def profile_projection(bin_section, axis: int = 1) -> list[Pair]:
    """Look for lines and words in the image via a profile projection.

    The image should be binarized because we are looking for blank rows (or columns)
    that delimit text.
    """
    data = np.array(bin_section).astype(np.int8)

    proj = data.sum(axis=axis)

    # This is a simple attempt to remove the threshold input argument
    # It should not work but it does... so far
    ordered = np.sort(proj)
    threshold = ordered[ordered.size // 2]

    mask = proj > threshold
    proj[mask] = 1
    proj[~mask] = 0

    pairs = []
    prev = 0
    top = 0
    for i, v in enumerate(proj):
        if v != prev:
            if v == 1:
                top = i
            else:
                pairs.append(Pair(top, i))
            prev = v

    return pairs
