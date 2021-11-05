"""Build lines of text from the OCR output."""
import unicodedata
from collections import Counter
from dataclasses import dataclass
from dataclasses import field
from functools import reduce
from itertools import groupby
from typing import Iterator

import regex as re

import digi_leap.pylib.line_align_py as la  # type: ignore
from digi_leap.pylib import line_align_subs
from digi_leap.pylib import vocab

# When there is no clear "winner" for a character in the multiple alignment of
# a set of strings I sort the characters by unicode category as a tiebreaker
_CATEGORY = {
    "Lu": 20,
    "Ll": 20,
    "Lt": 20,
    "Lm": 20,
    "Lo": 20,
    "Nd": 30,
    "Nl": 60,
    "No": 60,
    "Pc": 70,
    "Pd": 40,
    "Ps": 50,
    "Pe": 50,
    "Pi": 50,
    "Pf": 50,
    "Po": 10,
    "Sm": 99,
    "Sc": 90,
    "So": 90,
    "Zs": 80,
}

# As, above, but if a character has a category of "punctuation other" then I sort
# by the character itself
_PO = {
    ".": 1,
    ",": 2,
    ":": 2,
    ";": 2,
    "!": 5,
    '"': 5,
    "'": 5,
    "*": 5,
    "/": 5,
    "%": 6,
    "&": 6,
}

# Substitutions performed on a consensus sequence
SUBSTITUTIONS = [
    # Remove gaps
    ("⋄", ""),
    # Replace underscores with spaces
    ("_", " "),
    # Replace ™ trademark with a double quote
    ("™", '"'),
    # Remove space before some punctuation: x . -> x.
    (r"(\S)\s([;:.,\)\]\}])", r"\1\2"),
    # Trim internal spaces
    (r"\s\s+", " "),
    # Convert single capital letter, punctuation to capital dot: L' -> L.
    (r"(\p{L}\s\p{Lu})\p{Po}", r"\1."),
    # Add spaces around an &
    (r"(\w)&", r"\1 &"),
    (r"&(\w)", r"& \1"),
]


@dataclass
class Line:
    """Holds data for building an OCR line."""

    # This list is unordered and will contain several copies of the same text
    boxes: list[dict] = field(default_factory=list)

    def overlap(self, ocr_box, eps=1):
        """Find the vertical overlap between a line and an OCR bounding box.

        This is expressed as a fraction of the smallest height of the line
        & OCR bounding box.
        """
        last = self.boxes[-1]  # If self.boxes is empty then we have a bigger problem
        min_height = min(
            last["ocr_bottom"] - last["ocr_top"],
            ocr_box["ocr_bottom"] - ocr_box["ocr_top"],
        )
        y_min = max(last["ocr_top"], ocr_box["ocr_top"])
        y_max = min(last["ocr_bottom"], ocr_box["ocr_bottom"])
        inter = max(0, y_max - y_min)
        return inter / (min_height + eps)


def filter_boxes(
    ocr_boxes: list[dict],
    *,
    conf: float = 0.25,
    too_tall: float = 4.0,
    too_short: int = 10,
    too_thin: int = 10,
):
    """Remove problem bounding boxes from the list.

    Reasons for removing boxes include:
    - Remove bounding boxes with no text.
    - Remove boxes with a low confidence score (from the OCR engine) for the text.
    - Remove boxes that are too tall relative to the label.
    - Remove boxes that are really skinny or really short.
    """
    if len(ocr_boxes) < 2:
        return ocr_boxes

    filtered = []
    for box in ocr_boxes:
        text = box["ocr_text"].strip()
        width = box["ocr_right"] - box["ocr_left"]
        height = box["ocr_bottom"] - box["ocr_top"]

        if not text or width < too_thin or height < too_short:
            continue

        if box["conf"] >= conf and height / width <= too_tall:
            filtered.append(box)

    return filtered


def get_lines(ocr_boxes, vert_overlap=0.3):
    """Find lines of text from an OCR bounding boxes."""
    boxes = sorted(ocr_boxes, key=lambda b: b["ocr_left"])
    lines: list[Line] = []

    for box in boxes:
        overlap = [(r.overlap(box), r) for r in lines]
        overlap = sorted(overlap, key=lambda o: -o[0])

        if overlap and overlap[0][0] > vert_overlap:
            ln = overlap[0][1]
            ln.boxes.append(box)
        else:
            ln = Line()
            ln.boxes.append(box)
            lines.append(ln)

    lines = sorted(lines, key=lambda r: r.boxes[0]["ocr_top"])
    return lines


def get_copies(line: Line) -> list[str]:
    """Get the copies of text lines from the Line() object."""
    copies = []

    boxes = sorted(
        line.boxes, key=lambda b: (b["engine"], b["pipeline"], b["ocr_left"])
    )
    combos: Iterator = groupby(boxes, key=lambda b: (b["engine"], b["pipeline"]))

    for _, boxes in combos:
        text = " ".join([b["ocr_text"] for b in boxes])
        copies.append(text)

    return copies


def sort_copies(copies: list[str]) -> list[str]:
    """Sort the copies of the line by Levenshtein distance."""
    # levenshtein_all() returns a sorted array of tuples (score, index_1, index_2)
    if len(copies) <= 2:  # Sorting will do nothing in this case
        return copies

    distances = la.levenshtein_all(copies)
    _, i, j = distances.pop(0)

    hits = {i, j}
    ordered = [copies[i], copies[j]]

    while len(hits) < len(copies):
        for d, dist in enumerate(distances):
            i, j = dist[1:]
            if i in hits or j in hits:
                k = i if j in hits else j
                hits.add(k)
                ordered.append(copies[k])
                distances.pop(d)
                break
    return ordered


def align_copies(copies: list[str]) -> list[str]:
    """Do a multiple alignment of the text copies."""
    aligned = la.align_all(copies, line_align_subs.SUBS)
    return aligned


def _char_key(char):
    """Get the character sort order."""
    order = _CATEGORY.get(unicodedata.category(char), 100)
    order = _PO.get(char, order)
    return order, char


def _char_options(aligned):
    options = []
    str_len = len(aligned[0])

    for i in range(str_len):
        counts = Counter(s[i] for s in aligned).most_common()
        count = counts[0][1]
        chars = [c[0] for c in counts if c[1] == count]
        chars = sorted(chars, key=_char_key)  # Sort order is a fallback
        options.append(chars)
    return options


def _get_choices(options):
    """Recursively build all of the choices presented by a multiple alignment."""
    all_choices = []

    def _build_choices(opts, choice):
        if not opts:
            ln = "".join(choice)
            all_choices.append(ln)
            return
        for o in opts[0]:
            _build_choices(opts[1:], choice + [o])

    _build_choices(options, [])
    return all_choices


def _copies_key(choice):
    hits = vocab.hits(choice)
    count = sum(1 for c in choice if c not in "⋄_ ")
    return hits, count, choice


def choose_best_copy(copies):
    """Find the copy with the best score."""
    copies = sorted(copies, key=_copies_key, reverse=True)
    return copies[0]


def consensus(aligned: list[str], threshold=2 ** 16) -> str:
    """Build a consensus string from the aligned copies.

    Look at all options of the multiple alignment and choose
    the one that makes a string with the best score, or if there
    are too few or too many choices just look choose characters
    by their sort order.
    """
    options = _char_options(aligned)
    count = reduce(lambda x, y: x * len(y), options, 1)
    if count == 1 or count > threshold:
        cons = "".join([o[0] for o in options])
    else:
        choices = _get_choices(options)
        choices = sorted(choices, key=_copies_key, reverse=True)
        cons = choices[0]

    return cons


def substitute(cons):
    """Perform simple substitutions on a consensus string."""
    for old, new in SUBSTITUTIONS:
        cons = re.sub(old, new, cons)
    return cons


def spaces(ln):
    """Remove extra spaces in words.

    OCR engines will put spaces where there shouldn't be any. This is a simple
    scanner that looks for 2 non-words that make a new word when a space is removed.
    """
    words = vocab.word_split(ln)

    if len(words) < 3:
        return ln

    new = [words[0], words[1]]

    for i in range(2, len(words)):
        prev = words[i - 2]
        between = words[-1]
        curr = words[i]

        if (
            between.isspace()
            and prev + curr in vocab.WORDS
            and not (prev in vocab.WORDS or curr in vocab.WORDS)
        ):
            new.pop()  # Remove between
            new.pop()  # Remove prev
            new.append(prev + curr)
        else:
            new.append(words[i])

    return "".join(new)


def misspellings(line, min_len=3):
    """Word misspellings."""
    words = vocab.word_split(line)

    new = []

    for word in words:

        if not vocab.is_word(word):
            w = word

        elif len(word) < min_len or word in vocab.WORDS:
            w = word

        else:
            w = vocab.correction(word)

        new.append(w)

    return "".join(new)
