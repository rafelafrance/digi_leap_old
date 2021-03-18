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

    def __init__(self, label_recs, pad=0):
        # Store records by row to simplify calculations
        self.row_pad = pad
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
                    frag.font = font_
                    frag.text_size = font_.getsize(frag.text)

    def image_size(self):
        """Calculate the size of the entire image."""
        # Calculate each row's width & height
        self.row_heights = []
        widths = []

        for r, row in enumerate(self.rows):
            width = sum(r.text_size[0] for r in row)
            width += (len(row) - 1) * self.gutter.col
            width += self.margin.left + self.margin.right
            widths.append(width)

            row_height = max(r.text_size[1] for r in row)
            gutter_above = r != 0 and max(rec.line for rec in row) == 0
            gutter_above = int(gutter_above) * self.gutter.row
            self.row_heights.append((row_height + self.row_pad, gutter_above))

        # Calculate pate height
        height = sum(h[0] + h[1] for h in self.row_heights)
        height += self.margin.top + self.margin.bottom

        return max(widths), height

    def layout(self):
        """Layout the text images on the label."""
        self.image = Image.new(mode='RGB', size=self.image_size(), color='skyblue')

        y = self.margin.top

        for r, row in enumerate(self.rows):
            row_height, gutter_above = self.row_heights[r]

            x = self.margin.left
            y += gutter_above

            for frag in row:
                size = frag.text_size

                txt = Image.new(mode='RGB', size=size, color='white')
                draw = ImageDraw.Draw(txt)
                draw.text((0, 0), frag.text, font=frag.font, fill='black')

                self.image.paste(txt, (x, y, x + size[0], y + size[1]))

                x += frag.text_size[0] + self.gutter.col

            y += row_height
