"""Utilities and constants for working with fonts."""
from PIL import ImageFont

from digi_leap.pylib import consts

FONTS_DIR = consts.ROOT_DIR / "fonts"
FONT = FONTS_DIR / "SourceCodePro-Regular.ttf"
FONT2 = FONTS_DIR / "NotoSerif-Regular.ttf"
BASE_FONT_SIZE = 36


class FontDict(dict):
    """Allow easy resizing of fonts."""

    def __missing__(self, key):
        return ImageFont.truetype(str(FONT), key)


FONTS = FontDict()
BASE_FONT = ImageFont.truetype(str(FONT), BASE_FONT_SIZE)
