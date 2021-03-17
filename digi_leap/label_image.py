"""An object for generating label images from label text."""

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from digi_leap.label_fragment import Use, Writing, db2fragment


@dataclass
class Gutter:
    """Gutters between rows and columns within a row."""
    row: int = 8
    col: int = 8


@dataclass
class Margin:
    """Margins at the edges of a label."""
    left: int = 16
    top: int = 16
    right: int = 16
    bottom: int = 16


class LabelImage:
    """An object for generating label images from label text."""

    def __init__(self, label_recs):
        # Store records by row to simplify calculations
        self.recs = sorted(label_recs, key=lambda f: (f.row, f.col))
        self.frags = [db2fragment(r) for r in self.recs]
        self.rows = self.fragments_by_row()
        self.gutter = Gutter()
        self.margin = Margin()
        self.fonts = {}
        self.image = None
        self.row_heights = []

    def fragments_by_row(self):
        """Group fragments by ragged arrays of rows and columns."""
        rows = [list() for _ in range(self.recs[-1].row + 1)]
        for frag in self.frags:
            rows[frag.row].append(frag)
        return rows

    def set_font(self, use: Use, writing: Writing, font: Path, size: int) -> None:
        """Add a font for a use/writing combination."""
        font_ = ImageFont.truetype(font=str(font), size=size)
        self.fonts[(use, writing)] = font_
        for row in self.rows:
            for frag in row:
                if frag.use == use and frag.writing == writing:
                    frag.text_size = font_.getsize(frag.text)
                    frag.text_image = Image.new(
                        'RGB', size=frag.text_size, color='white')
                    frag.font = font_

    @property
    def image_size(self):
        """Calculate the size of the entire image."""
        # Calculate each row's width & height
        widths = []
        for row in self.rows:
            width = (len(row) - 1) * self.gutter.col
            width += self.margin.left + self.margin.right
            width += sum(r.text_size[0] for r in row)
            widths.append(width)

            self.row_heights.append(max(r.text_size[1] for r in row))

        # Final calculations
        height = (len(self.row_heights) - 1) * self.gutter.row
        height += self.margin.top + self.margin.bottom
        height += sum(self.row_heights)

        return max(widths), height

    def layout(self):
        """Layout the text images on the label."""
        self.image = Image.new('RGB', self.image_size, color='white')

        x, y = self.margin.top, self.margin.left

        for r, row in enumerate(self.rows):
            for frag in row:
                draw = ImageDraw.Draw(frag.text_image)
                draw.text((x, y), frag.text, font=frag.font, fill='black')
                self.image.paste(frag.text_image, (x, y))
                x += frag.text_size[0] + self.gutter.row
            y += self.row_heights[r] + self.gutter.col
