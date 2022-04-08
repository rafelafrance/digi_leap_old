"""Build lines of text from the OCR output."""
import collections
import dataclasses
import functools
import itertools
import unicodedata
from typing import Iterator

import regex as re


class OcrResults:
    """Constants for working with OCR results."""

    # When there is no clear "winner" for a character in the multiple alignment of
    # a set of strings I sort the characters by unicode category as a tiebreaker
    category = {
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

    # As, above, but if a character has a category of "punctuation other" then I
    # sort by the character itself
    po = {
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
    substitutions = [
        # Remove gaps
        ("⋄", ""),
        # Replace underscores with spaces
        ("_", " "),
        # Replace ™ trademark with a double quote
        ("™", '"'),
        # Remove space before some punctuation: x . -> x.
        (r"(\S)\s([;:.,\)\]\}])", r"\1\2"),
        # Compress spaces
        (r"\s\s+", " "),
        # Convert single capital letter, punctuation to capital dot: L' -> L.
        (r"(\p{L}\s\p{Lu})\p{Po}", r"\1."),
        # Add spaces around an ampersand &
        (r"(\w)&", r"\1 &"),
        (r"&(\w)", r"& \1"),
    ]


@dataclasses.dataclass
class Line:
    """Holds data for building one line from several OCR scans of the same text."""

    # This list is unordered and will contain several copies of the same text
    boxes: list[dict] = dataclasses.field(default_factory=list)


def find_overlap(line: Line, ocr_box, eps=1):
    """Find the vertical overlap between a line and an OCR bounding box.

    This is expressed as a fraction of the smallest height of the line
    & OCR bounding box.
    """
    last = line.boxes[-1]  # If self.boxes is empty then we have a bigger problem
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
        overlap = [(find_overlap(line, box), line) for line in lines]
        overlap = sorted(overlap, key=lambda o: -o[0])

        if overlap and overlap[0][0] > vert_overlap:
            line = overlap[0][1]
            line.boxes.append(box)
        else:
            line = Line()
            line.boxes.append(box)
            lines.append(line)

    lines = sorted(lines, key=lambda r: r.boxes[0]["ocr_top"])
    return lines


def get_copies(line: Line) -> list[str]:
    """Get the copies of text lines from the Line() object."""
    copies = []

    boxes = sorted(
        line.boxes, key=lambda b: (b["engine"], b["pipeline"], b["ocr_left"])
    )
    combos: Iterator = itertools.groupby(
        boxes, key=lambda b: (b["engine"], b["pipeline"])
    )

    for _, boxes in combos:
        text = " ".join([b["ocr_text"] for b in boxes])
        copies.append(text)

    return copies


def sort_copies(copies: list[str], line_align) -> list[str]:
    """Sort the copies of the line by Levenshtein distance."""
    if len(copies) <= 2:  # Sorting will do nothing in this case
        return copies

    # levenshtein_all() returns a sorted array of tuples (score, index_1, index_2)
    distances = line_align.levenshtein_all(copies)
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


def align_copies(copies: list[str], line_align) -> list[str]:
    """Do a multiple alignment of the text copies."""
    aligned = line_align.align(copies)
    return aligned


def _char_key(char):
    """Get the character sort order."""
    order = OcrResults.category.get(unicodedata.category(char), 100)
    order = OcrResults.po.get(char, order)
    return order, char


def _char_options(aligned):
    options = []
    str_len = len(aligned[0])

    for i in range(str_len):
        counts = collections.Counter(s[i] for s in aligned).most_common()
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


def _copies_key(choice, spell_well=None):
    hits = spell_well.hits(choice)
    count = sum(1 for c in choice if c not in "⋄_ ")
    return hits, count, choice


def choose_best_copy(copies, spell_well):
    """Find the copy with the best score."""
    key_func = functools.partial(_copies_key, spell_well=spell_well)
    copies = sorted(copies, key=key_func, reverse=True)
    return copies[0]


def consensus(aligned: list[str], spell_well, threshold=2 ** 16) -> str:
    """Build a consensus string from the aligned copies.

    Look at all options of the multiple alignment and choose
    the one that makes a string with the best score, or if there
    are too few or too many choices just look choose characters
    by their sort order.
    """
    key_func = functools.partial(_copies_key, spell_well=spell_well)
    options = _char_options(aligned)
    count = functools.reduce(lambda x, y: x * len(y), options, 1)
    if count == 1 or count > threshold:
        cons = "".join([o[0] for o in options])
    else:
        choices = _get_choices(options)
        choices = sorted(choices, key=key_func, reverse=True)
        cons = choices[0]

    return cons


def substitute(line: str) -> str:
    """Perform simple substitutions on a consensus string."""
    for old, new in OcrResults.substitutions:
        line = re.sub(old, new, line)
    return line


def add_spaces(line, spell_well, min_len: int = 3, min_freq: int = 10):
    """Add spaces between words.

    OCR engines will remove spaces between words. This function looks for a non-word
    and sees if adding a space will create 2 (or 1) word.
    For example: "SouthFlorida" becomes "South Florida".
    """
    tokens = spell_well.tokenize(line)

    new = []
    for token in tokens:
        if token.isspace() or spell_well.is_word(token) or len(token) < min_len:
            new.append(token)
        else:
            candidates = []
            for i in range(1, len(token) - 1):
                freq1 = spell_well.freq(token[:i])
                freq2 = spell_well.freq(token[i:])
                if freq1 >= min_freq or freq2 >= min_freq:
                    sum_ = freq1 + freq2
                    count = int(freq1 > 0) + int(freq2 > 0)
                    candidates.append((count, sum_, i))
            if candidates:
                i = sorted(candidates, reverse=True)[0][2]
                new.append(token[:i])
                new.append(" ")
                new.append(token[i:])
            else:
                new.append(token)

    return line


def remove_spaces(line, spell_well):
    """Remove extra spaces in words.

    OCR engines will put spaces where there shouldn't be any. This is a simple
    scanner that looks for 2 non-words that make a new word when a space is removed.
    For example: "w est" becomes "west".
    """
    tokens = spell_well.tokenize(line)

    if len(tokens) <= 2:
        return line

    new = tokens[:2]

    for i in range(2, len(tokens)):
        prev = tokens[i - 2]
        between = tokens[i - 1]
        curr = tokens[i]

        if (
            between.isspace()
            and spell_well.is_word(prev + curr)
            and not (spell_well.is_word(prev) or spell_well.is_word(curr))
        ):
            new.pop()  # Remove between
            new.pop()  # Remove prev
            new.append(prev + curr)
        else:
            new.append(tokens[i])

    return "".join(new)


def correct(line, spell_well):
    """Fix spell_well."""
    new = []
    for token in spell_well.tokenize(line):
        if spell_well.is_letters(token):
            token = spell_well.correct(token)
        new.append(token)
    return "".join(new)
