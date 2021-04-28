"""Functions for dealing with labels."""

from pathlib import Path

import numpy as np
import pytesseract
from PIL import Image, ImageFilter
from skimage import draw, io, morphology, util
from skimage.color import rgb2gray
from skimage.filters import threshold_sauvola
from skimage.transform import probabilistic_hough_line
from wand.image import Image as WImage


# Background colors
BLACK, WHITE = 1, 2


class Label:
    """Process labels."""

    config = ' '.join([
        '-l eng',
        "-c tessedit_char_blacklist='€«¢»£®'",
    ])

    near_horiz = np.deg2rad(np.linspace(-2.0, 2.0, num=5))
    near_vert = np.deg2rad(np.linspace(88.0, 92.0, num=5))
    near_horiz, near_vert = near_vert, near_horiz  # ?!

    def __init__(self, path: Path):
        self.path = path
        self.image = io.imread(str(path))
        self.data = rgb2gray(self.image)
        self.binarized = False
        self.background = WHITE

    def pipeline(self):
        """Process the label though the pipeline."""

    def invert_data(self, background):
        """Flip the image from black on white or vice versa.

        Some operations work better with white on black and others the reverse.
        """
        if background != self.background:
            self.data = util.invert(self.data)
            self.background = background

    def to_pil(self):
        """Convert the data into an image"""
        return Image.fromarray(self.data)

    def binarize(self, window_size: int = 11, k: float = 0.032):
        """Convert the image into a binary threshold form."""
        threshold = threshold_sauvola(self.data, window_size=window_size, k=k)
        self.data = self.data > threshold
        self.binarized = True

    def ocr(self):
        """OCR the image."""
        self.invert_data(background=WHITE)
        text = pytesseract.image_to_string(self.data, config=self.config)
        return text

    def find_horizontal_lines(self, line_length=100, line_gap=6):
        """Find horizontal lines (underlines, edges, etc.) on the label."""
        return self.find_lines(
            self.near_horiz, line_length=line_length, line_gap=line_gap)

    def find_vertical_lines(self, line_length=50, line_gap=6):
        """Find vertical lines (mostly edges) on the label."""
        return self.find_lines(
            self.near_vert, line_length=line_length, line_gap=line_gap)

    def find_lines(self, thetas, line_length=50, line_gap=6) -> list[tuple]:
        """Find lines on the label using the Hough Transform."""
        self.invert_data(background=BLACK)
        lines = probabilistic_hough_line(
            self.data,
            line_length=line_length,
            line_gap=line_gap,
            theta=thetas)
        return lines

    def remove_horiz_lines(self, lines, line_width=6, window=10, threshold=6):
        """Try to remove lines from the label."""
        rad = line_width // 2
        win = window // 2
        for line in lines:
            (c0, r0), (c1, r1) = line
            rr, cc = draw.line(r0, c0, r1, c1)

            for row, col in zip(rr, cc):
                count = self.data[row-win:row+win, col].sum()
                if count <= threshold:
                    self.data[row-rad:row+rad, col] = 0

    def deskew(self, threshold=0.4):
        """Try to straighten the image."""
        with WImage.from_array(self.data) as image:
            image.deskew(threshold)
            self.data = np.array(image)
            self.data = self.data[:, :, 0]

    def remove_salt(self, selem=None):
        """Try to remove noise from the image."""
        self.data = morphology.binary_opening(self.data, selem)

    def remove_soot(self, selem=None):
        """Try to remove noise from the image."""
        self.data = morphology.binary_closing(self.data, selem)

    def blur(self, radius=1):
        """Blur the image."""
        if self.binarized:
            raise ValueError('Blur before binarizing.')
        image = Image.fromarray(self.data)
        image = image.filter(ImageFilter.BoxBlur(radius))
        self.data = np.array(image)
