"""Utilities and constants for working with fonts."""

from digi_leap.pylib.const import ROOT_DIR
from PIL import ImageFont

FONTS_DIR = ROOT_DIR / "fonts"
FONT = FONTS_DIR / "print" / "Source_Code_Pro" / "SourceCodePro-Regular.ttf"
BASE_FONT_SIZE = 36


class FontDict(dict):
    """Allow easy resizing of fonts."""

    def __missing__(self, key):
        return ImageFont.truetype(str(FONT), key)


FONTS = FontDict()
BASE_FONT = ImageFont.truetype(str(FONT), BASE_FONT_SIZE)
