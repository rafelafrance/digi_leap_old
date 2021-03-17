"""An object for generating label images from label text."""

from PIL import Image, ImageDraw, ImageFont


class LabelImage:
    """An object for generating label images from label text."""

    def __init__(
            self,
            label_recs,
            label_size=(800, 500),
            col_gutter=8,
            row_gutter=8,
    ):
        self.recs = label_recs
        self.label_size = label_size
        self.col_gutter = col_gutter
        self.row_gutter = row_gutter
        self.fonts = {}
        self.image = None

    def set_font(self, use, writing, font, size):
        """Add a font for a use/writing combination."""
        font_ = ImageFont.truetype(font=str(font), size=size)
        self.fonts[(use, writing)] = font_
        for rec in self.recs:
            if rec['use'] == use and rec['writing'] == writing:
                rec['size'] = font_.getsize(rec['text'])
                rec['image'] = Image.new('RGB', size=rec['size'], color='white')

    def get_row_size(self, row):
        """Get the max height of the row."""
        return max(r['size'][1] for r in self.recs if r['row'] == row) if row else 0

    def layout(self):
        """Layout the text images on the label."""
        self.image = Image.new('RGB', self.label_size, color='white')

        x, y = 0, 0

        prev = {}

        for rec in self.recs:
            if rec['row'] != prev.get('row'):
                x = self.col_gutter
                y += self.row_gutter
                prev = rec
            font = self.fonts[(rec['use'], rec['writing'])]
            draw = ImageDraw.Draw(rec['image'])
            draw.text((x, y), text=rec['text'], font=font, fill='black')
            x += rec['size'][0]
            x += self.col_gutter
            self.image.paste(rec['image'])
        #         y += self.get_row_size()
        # txt = Image.new('RGB', size=)
        # draw = ImageDraw.Draw(image)
