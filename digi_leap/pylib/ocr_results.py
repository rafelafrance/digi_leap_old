"""Find lines of text in the OCR output."""
import statistics as stat
from dataclasses import dataclass
from dataclasses import field
from itertools import groupby
from typing import Iterator

import digi_leap.pylib.line_align_py as la  # type: ignore


@dataclass
class Line:
    """Holds data for building an OCR line."""

    boxes: list[dict] = field(default_factory=list)

    def overlap(self, ocr_box, eps=1):
        """Find the vertical overlap between a line and an OCR bounding box.

        This is expressed as a fraction of the smallest height of the line
        & OCR bounding box.
        """
        last = self.boxes[-1]  # If self.boxes is empty then we have a bigger problem
        min_height = min(
            last["bottom"] - last["top"], ocr_box["bottom"] - ocr_box["top"]
        )
        y_min = max(last["top"], ocr_box["top"])
        y_max = min(last["bottom"], ocr_box["bottom"])
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

    widths = [b["right"] - b["left"] for b in ocr_boxes]
    heights = [b["bottom"] - b["top"] for b in ocr_boxes]
    too_short = round(stat.mean(widths) - (std_devs * stat.stdev(widths)))
    too_thin = round(stat.mean(heights) - (std_devs * stat.stdev(heights)))

    filtered = []
    for box in ocr_boxes:
        width = box["right"] - box["left"]
        height = box["bottom"] - box["top"]
        text = box["text"].strip()

        if (
            text
            and (box["conf"] >= conf)
            and (too_tall > height > too_short)
            and width > too_thin
        ):
            filtered.append(box)

    return filtered


def get_lines(ocr_boxes, vert_overlap=0.3):
    """Find lines of text from an OCR bounding boxes."""
    boxes = sorted(ocr_boxes, key=lambda b: b["left"])
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

    lines = sorted(lines, key=lambda r: r.boxes[0]["top"])
    return lines


def get_copies(line: Line) -> list[str]:
    """Get the copies of text lines from the Line() object."""
    copies = []

    boxes = sorted(line.boxes, key=lambda b: (b["engine"], b["pipeline"], b["left"]))
    combos: Iterator = groupby(boxes, key=lambda b: (b["engine"], b["pipeline"]))

    for _, boxes in combos:
        text = " ".join([b["text"] for b in boxes])
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
