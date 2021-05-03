"""Functions for dealing with label images."""

import numpy as np
import numpy.typing as npt
import pytesseract
from PIL import Image
from scipy.ndimage import interpolation as inter
from skimage import draw
from skimage.filters import threshold_sauvola
from skimage.transform import probabilistic_hough_line

TESS_CONFIG = ' '.join([
    '-l eng',
    "-c tessedit_char_blacklist='€«¢»£®§{}'",
])

HORIZ_ANGLES = np.linspace(-2.0, 2.0, num=9)
NEAR_HORIZ = np.deg2rad(HORIZ_ANGLES)
NEAR_VERT = np.deg2rad(np.linspace(88.0, 92.0, num=9))
NEAR_HORIZ, NEAR_VERT = NEAR_VERT, NEAR_HORIZ  # ?!


def find_skew(label: npt.ArrayLike) -> float:
    """Find the skew of the label.

    This method is looking for sharp edges between the characters and spaces.
    It will work best with binary images.
    """
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
    if label.dtype == 'float64':
        return Image.fromarray(label * 255.0).convert('L')
    return Image.fromarray(label)


def binarize(
        label: npt.ArrayLike,
        window_size: int = 11,
        k: float = 0.032
) -> np.ndarray:
    """Convert the label into a binary threshold form."""
    threshold = threshold_sauvola(label, window_size=window_size, k=k)
    label = label < threshold
    return label


def ocr_text(label: npt.ArrayLike):
    """OCR the label and return text."""
    label = to_pil(label)
    text = pytesseract.image_to_string(label, config=TESS_CONFIG)
    return text


def ocr_data(label: npt.ArrayLike):
    """OCR the label and return tesseract data."""
    label = label.to_pil()
    boxes = pytesseract.image_to_data(label)
    return boxes


def find_lines(label: npt.ArrayLike, thetas, line_length=50, line_gap=6) -> list[tuple]:
    """Find lines on the label using the Hough Transform."""
    lines = probabilistic_hough_line(
        label,
        theta=thetas,
        line_length=line_length,
        line_gap=line_gap)
    return lines


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
