"""Functions for dealing with label images."""

from collections import namedtuple

import numpy as np
import numpy.typing as npt
import pytesseract
from PIL import Image
from scipy.ndimage import interpolation as inter
from skimage import draw
from skimage.filters import threshold_sauvola
from skimage.transform import probabilistic_hough_line

Pair = namedtuple('Pair', 'start end')
Where = namedtuple('Where', 'pos parity')

PADDING = 2  # How many pixels to pad a line or word
INSIDE_ROW = 2  # Only merge rows if they are this close
OUTSIDE_ROW = 100  # Only merge rows if they do not make a row this fat

TESS_CONFIG = ' '.join([
    '-l eng',
    "-c tessedit_char_blacklist='€«¢»£®§{}'",
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


# def rotate_image(label: Image, angle: float) -> Image:
#     """Rotate the image by a fractional degree."""
#     theta = np.deg2rad(angle)
#     cos, sin = np.cos(theta), np.sin(theta)
#     data = (cos, sin, 0.0, -sin, cos, 0.0)
#     rotated = image.transform(image.size, Image.AFFINE, data, fillcolor='black')
#     return rotated


def to_pil(label: npt.ArrayLike) -> Image:
    """Convert the label into a PIL image"""
    if label.dtype == 'float64':
        return Image.fromarray(label * 255.0).convert('L')
    return Image.fromarray(label)


def binarize(
        label: Image,
        window_size: int = 11,
        k: float = 0.032,
) -> np.ndarray:
    """Convert the label into a binary threshold form."""
    data = np.asarray(label).copy()
    threshold = threshold_sauvola(data, window_size=window_size, k=k)
    data = data < threshold
    return data


def ocr_text(label: npt.ArrayLike):
    """OCR the label and return text."""
    text = pytesseract.image_to_string(label, config=TESS_CONFIG)
    return text


def ocr_data(label: npt.ArrayLike):
    """OCR the label and return tesseract data."""
    data = pytesseract.image_to_data(label)
    return data


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


def profile_projection(
        bin_section: Image,
        threshold: int = 20,
        axis: int = 1,
        padding: int = PADDING,
) -> list[Pair]:
    """Look for lines and words in the image via a profile projection.

    Look for blank rows or columns of pixels that delimit lines of text or a word.
    """
    data = np.array(bin_section).astype(np.int8)

    proj = data.sum(axis=axis)
    proj = proj > threshold
    proj = proj.astype(int)

    prev = np.insert(proj[:-1], 0, 0)
    curr = np.insert(proj[1:], 0, 0)
    wheres = np.where(curr != prev)[0]
    wheres = wheres.tolist()

    splits = np.array_split(proj, wheres)

    wheres = wheres if wheres[0] == 0 else ([0] + wheres)
    wheres = [Where(w, s[0]) for w, s in zip(wheres, splits)]

    starts = [w.pos - padding for w in wheres if w.parity == 1]
    ends = [w.pos + padding for w in wheres if w.parity == 0][1:]
    pairs = [Pair(t - padding, b + padding) for t, b in zip(starts, ends)]

    return pairs


def overlapping_rows(old_rows: list[Pair]) -> list[Pair]:
    """Fix overlapping rows."""
    rows = [old_rows[0]]
    for row in old_rows[1:]:
        top, bottom = row
        prev_top, prev_bottom = rows[-1]
        if top < prev_bottom:
            mid = (top + prev_bottom) // 2
            rows.pop()
            rows.append(Pair(prev_top, mid))
            rows.append(Pair(mid, bottom))
        else:
            rows.append(row)
    return rows


def merge_rows(
        rows: list[Pair],
        *,
        inside_row: int = INSIDE_ROW,
        outside_row: int = OUTSIDE_ROW,
) -> list[Pair]:
    """Merge thin rows."""
    new_rows: list[Pair] = [rows[0]]

    for row in rows[1:]:
        top, bottom = row
        prev_top, prev_bottom = new_rows[-1]

        if (top - prev_bottom) <= inside_row and (bottom - prev_top) <= outside_row:
            new_rows.pop()
            new_rows.append(Pair(prev_top, bottom))
        else:
            new_rows.append(row)

    return new_rows
