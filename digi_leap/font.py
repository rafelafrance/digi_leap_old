"""Font utilities."""
from random import choice, randrange

from digi_leap.const import ROOT_DIR
from digi_leap.label_fragment import Use, Writing

FONT_DIR = ROOT_DIR / 'fonts'

TYPEWRITTEN_DIR = FONT_DIR / 'print'
HANDWRITTEN_DIR = FONT_DIR / 'cursive'

TYPEWRITTEN = [p for p in TYPEWRITTEN_DIR.glob('*/*.ttf')]
HANDWRITTEN = [p for p in HANDWRITTEN_DIR.glob('*/*.ttf')]

BOLD_FONTS = [p for p in TYPEWRITTEN if p.stem.casefold().find('bold') > -1]
NORMAL_FONTS = [p for p in TYPEWRITTEN if p.stem.casefold().find('bold') == -1]


def choose_label_fonts(label):
    """Set fonts for all label/writing combos."""
    combos = {(f.use, f.writing) for f in label.frags}

    for use, writing in combos:
        if writing == Writing.handwritten:
            font = choice(HANDWRITTEN)
            size = randrange(16, 25, 2)
        # elif writing == Writing.barcode:
        #     pass
        # elif writing == Writing.qrcode:
        #     pass

        elif use in (Use.field_label, Use.rights_holder, Use.title):
            font = choice(BOLD_FONTS)
            size = randrange(24, 33, 2)
        else:
            font = choice(NORMAL_FONTS)
            size = randrange(16, 25, 2)

        label.set_font(use, writing, font, size)
