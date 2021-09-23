"""Functions for manipulating OCR result ensembles."""

import re
from collections import defaultdict, namedtuple  # Counter
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict, Union

import pandas as pd

from . import box_calc as calc, vocab

DocText = namedtuple("DocText", "text ocr")


@dataclass
class BestScore:
    """Holds the best scores for a text ensemble."""

    text: str
    method: str
    score: float
    winners: list[str]


# Best = namedtuple("Best", "text method winners")


def get_results_df(path: Union[str, Path]) -> pd.DataFrame:
    """Get the data frame for the image.

    OCR results were stored as a CSV file. Create a data frame from the CSV, remove
    rows with blank text, and add the directory name to the data frame. The directory
    name is used later when building the text ensemble.
    """
    df = pd.read_csv(path).fillna("")
    df["ocr_dir"] = Path(path).parent.stem
    df.text = df.text.astype(str)
    df.text = df.text.str.strip()
    df = df.loc[df.text != ""]
    return df


def filter_bounding_boxes(
    df: pd.DataFrame,
    image_height: int,
    conf: float = 0.25,
    height_threshold: float = 0.25,
    std_devs: float = 2.0,
) -> pd.DataFrame:
    """Remove problem bounding boxes from the data frame.

    Excuses for removing boxes include:
    - Remove bounding boxes with no text.
    - Remove boxes with a low confidence score (from the OCR engine) for the text.
    - Remove boxes that are too tall relative to the label.
    - Remove boxes that are really skinny or really short.
    """
    df["width"] = df.right - df.left + 1
    df["height"] = df.bottom - df.top + 1

    # Remove boxes with nothing in them
    df = df.loc[df.text != ""]

    # Remove boxes with low confidence
    df = df.loc[df.conf > conf]

    # Remove boxes that are too tall
    thresh_height = round(image_height * height_threshold)
    df = df.loc[df.height < thresh_height]

    # Remove boxes that are very thin or very short
    thresh_width = round(df.width.mean() - (std_devs * df.width.std()))
    thresh_height = round(df.height.mean() - (std_devs * df.height.std()))
    df = df.loc[(df.width > thresh_width) & (df.height > thresh_height)]

    return df


def text_hits(text: str) -> int:
    """Count the number of words in the text that are in our corpus.

    A hit is:
    - A direct match in the vocabulary
    - A number like: 99.99
    - A data like: 1/22/34 or 11-2-34
    """
    words = text.lower().split()
    hits = sum(1 for w in words if re.sub(r"\W", "", w) in vocab.VOCAB and len(w) > 2)
    hits += sum(1 for w in words if re.match(r"^\d+[.,]?\d*$", w))
    hits += sum(1 for w in words if re.match(r"^\d\d?[/-]\d\d?[/-]\d\d$", w))
    return hits


def reconcile_text(doc_texts: list[DocText]) -> BestScore:
    """Find the single "best" text string from a list of similar texts.

    First we look for the most common text string in the list. If that
    occurs more than half of the time, we return that. Otherwise, we look
    for a string that contains the most words that have a vocabulary hit.
    """
    if not doc_texts:
        return BestScore("", "None", 0.0, [])

    # First look if a text appears in the majority of ocr documents
    counts = defaultdict(list)
    for text, ocr in doc_texts:
        text = re.sub(r"\s([.,:])", r"\1", text)  # Remove leading space from punct
        counts[text].append(ocr)

    bests = [
        BestScore(text, "majority", len(ocr) / len(doc_texts), ocr)
        for text, ocr in sorted(counts.items(), key=lambda x: len(x[1]))
    ]

    if bests[0].score >= 0.5 and len(bests[0].winners) > 1:
        return bests[0]

    # Fallback to looking for the text(s) with the best score
    scores: DefaultDict[float, list[DocText]] = defaultdict(list)
    for doc_text in doc_texts:
        words = doc_text.text.split()
        hits = text_hits(doc_text.text)
        count = len(words)
        score = (hits / count) if count > 0 else 0.0
        scores[score].append(doc_text)

    top = [(s, d) for s, d in sorted(scores.items(), key=lambda i: -i[0])]
    score, doc_text = top[0]
    text = doc_text[0].text  # If there are equal scores choose the first text
    winners = [d.ocr for d in doc_text]
    return BestScore(text, "score", score, winners)


def merge_bounding_boxes(df: pd.DataFrame, threshold: float = 0.50) -> pd.DataFrame:
    """Merge overlapping bounding boxes and create a new data frame.

    1) Find boxes that overlap and assign overlapping boxes to a group
    2) For each overlap group find boxes from the same document. This is flagged by
       by the OCR dir and NOT the file name because, by definition, each ensemble
       has identical files names but come from different directories.
        a) Put the text for each document group in left to right order & join the text.
    3) Merge the bounding boxes into a single bounding box. One per each OCR document.
    4) Find the "best" text for the new bounding box. "Best" is relative to the other
       documents.
    """
    boxes = df[["left", "top", "right", "bottom"]].to_numpy()
    groups = calc.small_box_overlap(boxes, threshold=threshold)
    df["group"] = groups

    merged = []
    # First find everything that overlaps in all docs
    for g, box_group in df.groupby("group"):
        texts = []
        # Now combine texts by doc
        for s, subgroup in box_group.groupby("ocr_dir"):
            subgroup = subgroup.sort_values("left")
            text = " ".join(subgroup.text)
            texts.append(DocText(text, str(s)))

        # Find the "best" text & the docs with it
        best_score = reconcile_text(texts)

        merged.append(
            {
                "left": box_group.left.min(),
                "top": box_group.top.min(),
                "right": box_group.right.max(),
                "bottom": box_group.bottom.max(),
                "text": best_score.text,
                "ocr_dir": box_group.ocr_dir.iloc[0],
                "method": best_score.method,
                "winners": best_score.winners,
                "score": best_score.score,
            }
        )

    df = pd.DataFrame(merged)
    df.text = df.text.astype(str)
    return df


def merge_rows_of_text(df: pd.DataFrame) -> pd.DataFrame:
    """Merge bounding boxes on the same row of text into a single bounding box."""
    df = df.groupby("row").agg(
        {
            "left": "min",
            "top": "min",
            "right": "max",
            "bottom": "max",
            "text": " ".join,
        }
    )
    df = df.sort_values("top").reset_index(drop=True)
    df["row"] = df.index + 1
    return df
