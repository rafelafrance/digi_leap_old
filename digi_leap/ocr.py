"""OCR images."""

import re
from pathlib import Path

import numpy as np
import pytesseract
from PIL import Image, ImageOps
from scipy import ndimage
from skimage import filters, morphology as morph

from digi_leap import label_image as li
from digi_leap.ocr_score import ocr_score

# TODO: Constants like this should get calculated
# For threshold_sauvola
WINDOW_SIZE = 11
K = 0.032

# For remove_small_objects
MIN_SIZE = 64

# For ImageOps.scale
MIN_DIM = 512
FACTOR = 2.0


def ocr_label(path: Path):
    """Try to OCR the image."""
    image = Image.open(path).convert('L')

    # ################################################################
    # Try the unmodified label

    action = 'did nothing'

    best = ocr_score(image)

    if best.is_ok:
        return best.update(path, action)

    # ################################################################
    # Try a bigger label

    action = f'scaled by: {FACTOR}'

    bigger = ImageOps.scale(image, FACTOR)
    score = ocr_score(bigger)

    if image.width < MIN_DIM or image.height < MIN_DIM:
        image = bigger
        best.log(action)

    if score > best:
        image = bigger
        best = score
        best.log(action)
        if best.is_ok:
            return best.update(path, action)

    # ################################################################
    # Try to orient the label

    osd = pytesseract.image_to_osd(image)
    angle = int(re.search(r'degrees:\s*(\d+)', osd).group(1))

    action = f'rotated by: {angle}'

    data = np.asarray(image).copy()

    if angle != 0:
        rotated = ndimage.rotate(data, int(angle), mode='nearest')
        rotated = li.to_pil(rotated)
        score = ocr_score(rotated)

        if score > best:
            image = rotated
            best = score
            best.log(action)
            if best.is_ok:
                return best.update(path, action)

    # ################################################################
    # Try converting the image to binary

    action = f'sauvola threshold window size = {WINDOW_SIZE} K = {K}'

    binary = np.asarray(image).copy()
    threshold = filters.threshold_sauvola(binary, window_size=WINDOW_SIZE, k=K)
    binary = binary < threshold

    temp = li.to_pil(binary)
    score = ocr_score(temp)

    if score > best:
        best = score
        score.log(action)
        if score.is_ok:
            return score.update(path, action)

    # ################################################################
    # Try to remove small objects

    action = f'removed small objects min_size = {MIN_SIZE}'

    cleaned = morph.remove_small_objects(binary, min_size=MIN_SIZE)
    score = ocr_score(li.to_pil(cleaned))

    if score > best:
        binary = cleaned
        best = score
        score.log(action)
        if score.is_ok:
            return score.update(path, action)

    # ################################################################
    # Try opening holes

    action = f'binary opening'

    cleaned = morph.binary_opening(binary)
    score = ocr_score(li.to_pil(cleaned))

    if score > best:
        # binary = cleaned
        best = score
        score.log(action)
        if score.is_ok:
            return score.update(path, action)

    # ################################################################
    # Try dissecting the label

    # ################################################################
    # Try to correct skew on each label part

    # ################################################################
    # Try to remove horizontal lines on each label part

    # ################################################################
    # Nothing worked

    return best.update(path, 'fail')
