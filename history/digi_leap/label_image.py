"""An object for generating label images from label text."""

from collections import namedtuple
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from history.digi_leap.label_fragment import Size, Use, Writing, db2fragment

Gutter = namedtuple('Gutter', 'row col')
Margin = namedtuple('Margin', 'left top right bottom')


class LabelImage:
    """An object for generating label images from label text."""

    def __init__(self, label_recs):
        # Store records by row to simplify calculations
        self.recs = sorted(label_recs, key=lambda f: (f.row, f.col))
        self.frags = [db2fragment(r) for r in self.recs]
        self.rows = self.fragments_by_row()
        self.label_type = self.frags[0].label_type
        self.label_id = self.frags[0].label_id
        self.row_pad = 0
        self.gutter = Gutter(8, 8)
        self.margin = Margin(16, 16, 16, 16)
        self.fonts = {}
        self.image_y = None
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
                    width, height = font_.getsize(frag.text)
                    frag.text_size = Size(width, height)

    def image_size(self):
        """Calculate the size of the entire image."""
        # Calculate each row's width & height
        self.row_heights = []
        widths = []

        for r, row in enumerate(self.rows):
            width = sum(r.text_size.width for r in row)
            width += (len(row) - 1) * self.gutter.col
            width += self.margin.left + self.margin.right
            widths.append(width)

            row_height = max(r.text_size.height for r in row)
            gutter_above = r != 0 and max(rec.line for rec in row) == 0
            gutter_above = int(gutter_above) * self.gutter.row
            self.row_heights.append((row_height + self.row_pad, gutter_above))

        # Calculate pate height
        height = sum(h[0] + h[1] for h in self.row_heights)
        height += self.margin.top + self.margin.bottom

        return Size(max(widths), height)

    def layout(self):
        """Layout the text images on the label."""
        image_size = self.image_size()
        self.image_y = Image.new(mode='RGB', size=image_size, color='white')

        draw = ImageDraw.Draw(self.image_y)
        m = self.margin
        l, t, r, b = m.left // 2, m.top // 2, m.right // 2, m.bottom // 2
        draw.rectangle(
            (l, t, image_size.width - r, image_size.height - b),
            outline='darkgray')

        y = self.margin.top

        for r, row in enumerate(self.rows):
            row_height, gutter_above = self.row_heights[r]

            x = self.margin.left
            y += gutter_above

            for frag in row:
                txt = Image.new(mode='RGB', size=frag.text_size, color='white')
                draw = ImageDraw.Draw(txt)
                draw.text((0, 0), frag.text, font=frag.font, fill='black')

                if frag.use == Use.title:
                    new_x = (image_size.width - frag.text_size.width) // 2
                    self.image_y.paste(txt, (new_x, y))
                else:
                    self.image_y.paste(txt, (x, y))

                x += frag.text_size.width + self.gutter.col

            y += row_height
