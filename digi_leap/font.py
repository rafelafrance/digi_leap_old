"""Font utilities."""
from random import choice, randrange

from digi_leap.const import ROOT_DIR

FONT_DIR = ROOT_DIR / 'fonts'

TYPEWRITTEN_DIR = FONT_DIR / 'print'
HANDWRITTEN_DIR = FONT_DIR / 'cursive'

TYPEWRITTEN = [p for p in TYPEWRITTEN_DIR.glob('*/*.ttf')]
HANDWRITTEN = [p for p in HANDWRITTEN_DIR.glob('*/*.ttf')]

BOLD_FONTS = [p for p in TYPEWRITTEN if p.stem.casefold().find('bold') > -1]
NORMAL_FONTS = [p for p in TYPEWRITTEN if p.stem.casefold().find('bold') == -1]


def choose_label_fonts(label):
    """Set fonts for all label/writing combos."""
    combos = {(r['use'], r['writing']) for r in label.recs}

    for use, writing in combos:
        if writing == 'handwritten':
            font = choice(HANDWRITTEN)
            size = randrange(26, 35, 2)
        # elif writing == 'barcode':
        #     pass
        # elif writing == 'qrcode':
        #     pass
        elif use in ('label_field', 'rights_holder', 'title'):
            font = choice(BOLD_FONTS)
            size = randrange(34, 43, 2)
        else:
            font = choice(NORMAL_FONTS)
            size = randrange(26, 35, 2)

        label.set_font(use, writing, font, size)
