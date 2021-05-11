"""Handle OCR scores."""
import re
import string
import textwrap
from dataclasses import dataclass, field

import enchant
import pytesseract

from digi_leap import label_image as li
from digi_leap.const import DATA_DIR

OK = 90.0  # 90% words spelled correctly is considered good enough
MIN_WORDS = 20  # At least this many correctly spelled words should be in a label

PUNCT = re.escape(string.punctuation)
SPLIT = re.compile(rf'([\s{PUNCT}]+)')

ALLOW = {'.)', '.]'}
LANG = 'en_US'
EXTRA_VOCAB = DATA_DIR / 'custom_vocab.txt'
VOCAB = enchant.DictWithPWL(LANG, str(EXTRA_VOCAB))


@dataclass(order=True)
class OCRScore:
    """Handle OCR scores."""

    found: int = 0
    total: int = 0
    file: str = ''
    stem: str = ''
    method: list[str] = field(default_factory=list)
    text: str = ''

    @property
    def score(self):
        """Score the results."""
        return self.found, self.percent

    @property
    def is_ok(self):
        """Is the score good enough?"""
        return self.percent >= OK and self.found >= MIN_WORDS

    @property
    def percent(self):
        """Calculate the percent of found words."""
        per = self.found / self.total if self.total != 0 else 0.0
        return round(per * 100.0, 2)

    def __str__(self):
        return textwrap.dedent(f"""
        {self.score=}
        {self.found=}
        {self.percent=}
        {self.total=}
        {self.stem=}
        {self.method=}
        """)

    def update(self, path, method):
        """Update the score."""
        self.file = str(path)
        self.stem = path.stem
        self.log(method)
        return self

    def log(self, action):
        """Log the OCR action."""
        if not self.method or action != self.method[-1]:
            self.method.append(action)


def ocr_score(image):
    """Score OCR results using the spell checker as a proxy for quality."""
    text = pytesseract.image_to_string(image, config=li.TESS_CONFIG)
    text = re.sub(r'[\r\f]', '\n', text)
    text = re.sub(r'(\n\s*){3,}', '\n\n', text)
    text = text.strip()

    words = [x for w in SPLIT.split(text) if (x := w.strip())]

    found = sum(1 for w in words if VOCAB.check(w)
                or len(w) == 1 or w in ALLOW)

    return OCRScore(
        total=len(words),
        found=found,
        text=text,
    )
