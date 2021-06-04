"""Handle OCR scores."""
import csv
import re
import string
import textwrap
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Optional

import easyocr
import enchant
import pytesseract
from PIL import Image

from digi_leap.const import CHAR_BLACKLIST, DATA_DIR, TESS_CONFIG
from digi_leap.util import to_opencv

MIN_WORDS = 20  # At least this many correctly spelled words should be in a label
OK = 60.0  # If this percent of words are spelled correctly it's considered good enough
MIN_LEN = 3  # Shorter words have a higher probability of being randomly generated

PUNCT = re.escape(string.punctuation)
SPLIT = re.compile(rf'([\s{PUNCT}]+)')

ALLOW = {'.)', '.]'}
LANG = 'en_US'
EXTRA_VOCAB = DATA_DIR / 'custom_vocab.txt'
VOCAB = enchant.DictWithPWL(LANG, str(EXTRA_VOCAB))

EASY_OCR = easyocr.Reader(['en'])


class BBox:
    """A bounding box for an OCR area."""

    def __init__(self, **kwargs):
        self.left: int = kwargs.get('left', 999999)
        self.top: int = kwargs.get('top', 999999)
        self.right: int = kwargs.get('right', -1)
        self.bottom: int = kwargs.get('bottom', -1)
        self.text: str = kwargs.get('text', '')
        self.conf: float = kwargs.get('conf', 0.0)

    @property
    def empty(self):
        return self.right != -1

    @property
    def height(self):
        return self.bottom - self.top + 1

    @property
    def width(self):
        return self.right - self.left + 1

    def as_list(self):
        """Convert to a list of coordinates."""
        return [self.left, self.top, self.right, self.bottom]


@dataclass(order=True)
class OCRScore:
    """Handle OCR scores."""

    found: int = 0
    total: int = 0
    file: str = ''
    stem: str = ''
    method: list[str] = field(default_factory=list)
    engine: str = ''
    text: str = ''
    data: Optional[list[BBox]] = None

    @property
    def score(self) -> tuple[int, float]:
        """Score the results."""
        return self.found, self.percent

    @property
    def is_ok(self) -> bool:
        """Is the score good enough?"""
        return self.percent >= OK and self.found >= MIN_WORDS

    @property
    def percent(self) -> float:
        """Calculate the percent of found words."""
        per = self.found / self.total if self.total != 0 else 0.0
        return round(per * 100.0, 2)

    def __str__(self) -> str:
        return textwrap.dedent(f"""
        {self.score=}
        {self.found=}
        {self.percent=}
        {self.total=}
        {self.stem=}
        {self.method=}
        {self.engine=}
        """)

    def update(self, path: Path, method) -> 'OCRScore':
        """Update the score."""
        self.file = str(path)
        self.stem = path.stem
        self.log(method)
        return self

    def log(self, action: str) -> None:
        """Log the OCR action."""
        if not self.method or action != self.method[-1]:
            self.method.append(action)


def score_tesseract(image: Image) -> OCRScore:
    """Score the results of using the tesseract OCR engine."""
    raw = pytesseract.image_to_data(image, config=TESS_CONFIG)
    data = []
    with StringIO(raw) as in_file:
        rows = [r for r in csv.DictReader(in_file, delimiter='\t')]
        if len(rows) < 5:
            return score_text([], 'tesseract')
        for row in rows:
            conf = float(row['conf'])
            if conf < 0:  # Is an outer box that surrounds inner boxes
                continue
            if row['text'].find('\n') > -1:
                continue
            left = int(row['left'])
            top = int(row['top'])
            data.append(BBox(
                text=row['text'],
                conf=conf / 100.0,
                left=left,
                top=top,
                right=left + int(row['width']) - 1,
                bottom=top + int(row['height']) - 1,
            ))
    return score_text(data, 'tesseract')


def score_easyocr(image) -> OCRScore:
    """Score the results of using the easyocr engine."""
    image = to_opencv(image)
    raw = EASY_OCR.readtext(image, blocklist=CHAR_BLACKLIST)
    data = []
    for item in raw:
        pos = item[0]
        data.append(BBox(
            text=item[1],
            conf=item[2],
            left=pos[0][0],
            top=pos[0][1],
            right=pos[1][0],
            bottom=pos[2][1],
        ))
    return score_text(data, 'easyocr')


def score_text(data: list[dict], engine: str) -> OCRScore:
    """Score the output from the OCR."""
    text = ' '.join(d.text for d in data)
    words = [x for w in SPLIT.split(text) if (x := w.strip())]
    found = sum(1 for w in words if len(w) >= MIN_LEN and VOCAB.check(w))
    return OCRScore(
        total=len(words),
        found=found,
        engine=engine,
        text=text,
        data=data,
    )
