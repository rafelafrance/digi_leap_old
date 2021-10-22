"""Build lines of text from the OCR output."""
import statistics as stat
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

SUBSTITUTIONS = [
    # Remove gaps
    ("⋄", ""),
    # Replace underscores with spaces
    ("_", " "),
    # Replace ™ trademark with a double quote
    ("™", '"'),
    # Remove space before some punct: x . -> x.
    (r"(\S)\s([;:.,\)\]\}])", r"\1\2"),
    # Trim internal spaces
    (r"\s\s+", " "),
    # Convert single capital letter, punct to capital dot: L' -> L.
    (r"(\p{L}\s\p{Lu})\p{Po}", r"\1."),
    # Add spaces around an &
    (r"(\w)&", r"\1 &"),
    (r"&(\w)", r"& \1"),
]


@dataclass
class Line:
    """Holds data for building an OCR line."""

    # This list is unordered and may contain several copies of the same text
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
    image_height: int,
    conf: float = 0.25,
    std_devs: float = 2.0,
    height_fract: float = 0.25,
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

    too_tall = round(image_height * height_fract)

    widths = [b["ocr_right"] - b["ocr_left"] for b in ocr_boxes]
    heights = [b["ocr_bottom"] - b["ocr_top"] for b in ocr_boxes]
    too_short = round(stat.mean(widths) - (std_devs * stat.stdev(widths)))
    too_thin = round(stat.mean(heights) - (std_devs * stat.stdev(heights)))

    filtered = []
    for box in ocr_boxes:
        width = box["ocr_right"] - box["ocr_left"]
        height = box["ocr_bottom"] - box["ocr_top"]
        text = box["ocr_text"].strip()

        if (
            text
            and width > 1
            and height > 1
            and (box["conf"] >= conf)
            and (too_tall > height > too_short)
            and width > too_thin
        ):
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
    if len(copies) <= 2:  # Sorting will do nothing
        return copies

    distances = la.levenshtein_all(copies)
    _, i, j = distances.pop(0)

    hits = {i, j}
    ordered = [copies[i], copies[j]]

    while len(hits) < len(copies):
        for d, dist in enumerate(distances):
            i, j = dist[1:]
            if i in hits and j not in hits:
                hits.add(j)
                ordered.append(copies[j])
                distances.pop(d)
                break
            elif j in hits and i not in hits:
                hits.add(i)
                ordered.append(copies[i])
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


def _word_consensus_key(choice):
    hits = vocab.vocab_hits(choice)
    count = sum(1 for c in choice if c not in "⋄_ ")
    return hits, -count


def _word_consensus(options):
    choices = _get_choices(options)
    choices = sorted(choices, key=_word_consensus_key)
    return choices[0]


def consensus(aligned: list[str], threshold=2 ** 16) -> str:
    """Build a consensus string from the aligned copies."""
    options = _char_options(aligned)
    count = reduce(lambda x, y: x * len(y), options, 1)
    if count == 1 or count > threshold:
        cons = "".join([o[0] for o in options])
    else:
        cons = _word_consensus(options)

    return cons


def substitute(cons):
    """Perform simple substitutions on a consensus string."""
    for old, new in SUBSTITUTIONS:
        cons = re.sub(old, new, cons)
    return cons


def spaces(ln):
    """Remove extra spaces in words."""
    words = ln.split()

    if not words:
        return ln

    new = [words[0]]
    for i in range(1, len(words)):
        prev = re.sub(r"^\W+", "", words[i - 1])
        curr = re.sub(r"\W+$", "", words[i])

        prev_in_vocab = vocab.in_vocab(vocab.ALL_WORDS, prev)
        curr_in_vocab = vocab.in_vocab(vocab.ALL_WORDS, curr)
        combo_in_vocab = vocab.in_vocab(vocab.ALL_WORDS, prev + curr)

        if combo_in_vocab and not prev_in_vocab and not curr_in_vocab:
            new.pop()
            new.append(words[i - 1] + words[i])
        else:
            new.append(words[i])

    return " ".join(new)
