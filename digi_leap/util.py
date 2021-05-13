"""Common utilities."""

import numpy as np
from PIL import Image
from numpy import typing as npt
from scipy.ndimage import interpolation as interp
from skimage.transform import probabilistic_hough_line

from digi_leap.const import HORIZ_ANGLES


def to_pil(label: npt.ArrayLike) -> Image:
    """Convert the label into a PIL image"""
    if len(label.shape) == 3:
        label = label[:, :, 0]
    if label.dtype == 'float64':
        return Image.fromarray(label * 255.0).convert('L')
    return Image.fromarray(label)


def to_opencv(image):
    """Convert the image into a format opencv can handle."""
    image = np.asarray(image)
    if image.dtype == 'bool':
        return (image * 255).astype('uint8')
    return image


def iou(box1, box2):
    """Calculate the intersection over union of a pair of boxes."""
    x0 = max(box1[0], box2[0])
    y0 = max(box1[1], box2[1])
    x1 = min(box1[2], box2[2])
    y1 = min(box1[3], box2[3])
    inter = max(0, x1 - x0 + 1) * max(0, y1 - y0 + 1)
    area1 = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    area2 = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
    return inter / (area1 + area2 - inter)


def nms(boxes, threshold=0.3, scores=None):
    """Remove overlapping boxes via non-maximum suppression.

    Modified from Matlab code:
    https://www.computervisionblog.com/2011/08/blazing-fast-nmsm-from-exemplar-svm.html
    """
    if len(boxes) == 0:
        return []

    if boxes.dtype.kind == 'i':
        boxes = boxes.astype('float64')

    # Simplify access to box components
    x0, y0, x1, y1 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]

    area = (x1 - x0 + 1) * (y1 - y0 + 1)

    idx = scores if scores else area
    idx = np.argsort(idx)

    non_overlapping = []
    while len(idx) > 0:
        curr = idx[-1]  # Work with end of list so slice indexing will work as is
        non_overlapping.insert(0, curr)  # Preserve order

        # Get interior (overlap) coordinates
        xx0 = np.maximum(x0[curr], x0[idx[:-1]])
        yy0 = np.maximum(y0[curr], y0[idx[:-1]])
        xx1 = np.minimum(x1[curr], x1[idx[:-1]])
        yy1 = np.minimum(y1[curr], y1[idx[:-1]])

        # Get the intersection
        overlap = np.maximum(0, xx1 - xx0 + 1) * np.maximum(0, yy1 - yy0 + 1)
        overlap = overlap / area[idx[:-1]]

        # Find intersections larger than threshold & remove them
        overlap = np.where(overlap > threshold)[0]
        delete = np.concatenate(([-1], overlap))
        idx = np.delete(idx, delete)

    return boxes[non_overlapping].astype('int')


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
