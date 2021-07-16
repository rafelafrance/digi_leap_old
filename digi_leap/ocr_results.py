"""Functions for manipulaing OCR result ensembles."""

import re
from collections import Counter
from pathlib import Path
from typing import Union

import nltk
import numpy as np
import pandas as pd
from nltk.corpus import words

from digi_leap.box_calc import small_box_overlap


def get_nltk_words():
    """Get words from the NLTK corpus."""
    nltk.download("words")


def get_vocab() -> set[str]:
    """Get the vocabulary used for scoring OCR quality."""
    vocab_dir = Path("..") / "data" / "vocab"

    vocab = set()

    with open(vocab_dir / "plant_taxa.txt") as in_file:
        vocab |= {v.strip().lower() for v in in_file.readlines() if len(v) > 1}

    vocab |= {w.lower() for w in words.words() if len(w) > 1}

    return vocab


def get_results_df(path: Union[str, Path]) -> pd.DataFrame:
    """Get the data frame from the image."""
    df = pd.read_csv(path).fillna("")
    df["ocr_dir"] = Path(path).parent.stem
    df.text = df.text.str.strip()
    df = df.loc[df.text != ""]
    return df


def filter_bounding_boxes(
    df: pd.DataFrame,
    image_height: int,
    conf: float = 0.25,
    height_threshold: float = 0.25,
    std_devs: float = 3.0,
) -> pd.DataFrame:
    """Remove problem bounding boxes from the data frame."""
    df["width"] = df.right - df.left + 1
    df["height"] = df.bottom - df.top + 1

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


def reconcile_text(texts: list[str], vocab: set[str]) -> str:
    """Find the single "best" text string from a list of similar texts.

    First we look for the most common text string in the list. If that
    occurs more than half of the time, we return that. Otherwise, we
    look for a string that contains the most words from the vocab.
    """
    if not texts:
        return ""

    texts = [re.sub(r"\s([.,:])", r"\1", t) for t in texts]
    counts = Counter(texts)
    counts = [(c[1], len(c[0]), c[0]) for c in counts.most_common()]
    counts = sorted(counts, reverse=True)
    best = counts[0]

    if best[0] > len(texts) / 2:
        return best[2]

    scores = []
    for t, text in enumerate(texts):
        words = text.split()
        hits = sum(1 for w in words if re.sub(r"\S", "", w) in vocab)
        hits += sum(1 for w in words if re.match(r"^\d+[.,]?\d*$", w))
        hits += sum(1 for w in words if re.match(r"^\d{1,2}[/-]\d{1,2}[/-]\d{1,2}$", w))
        count = len(words)
        scores.append((hits / count, count, t))

    best = sorted(scores, reverse=True)[0]
    return texts[best[2]]


def merge_bounding_boxes(df: pd.DataFrame, vocab: set[str]) -> pd.DataFrame:
    """Merge overlapping bounding boxes and create a new data frame."""
    boxes = df[["left", "top", "right", "bottom"]].to_numpy()
    groups = small_box_overlap(boxes)
    df["group"] = np.absolute(groups)

    merged = []
    for g, box_group in df.groupby("group"):
        texts = []
        for s, subgroup in box_group.groupby("ocr_dir"):
            subgroup = subgroup.sort_values("left")
            text = " ".join(str(i.text) for _, i in subgroup.iterrows())
            texts.append(text)

        merged.append(
            {
                "left": box_group.left.min(),
                "top": box_group.top.min(),
                "right": box_group.right.max(),
                "bottom": box_group.bottom.max(),
                "text": reconcile_text(texts, vocab),
            }
        )

    df = pd.DataFrame(merged)
    return df


def find_rows_of_text(df: pd.DataFrame, image_height: int) -> pd.DataFrame:
    """Find rows of text in the label and mark what row each box belongs to."""
    df = df.sort_values(["left", "top"])
    df["row"] = 0

    rows = {}
    for idx, box in df.iterrows():
        mid = (box.top + box.bottom) // 2
        if row := [r for r, b in rows.items() if b[0] <= mid <= b[1]]:
            row = row[0]
        else:
            row = len(rows) + 1
        rows[row] = (box.top, box.bottom)
        df.at[idx, "row"] = row

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


def straighten_rows_of_text(df: pd.DataFrame) -> pd.DataFrame:
    """Align bounding boxes on the same row of text to the same top and bottom."""
    for r, boxes in df.groupby("row"):
        df.loc[boxes.index, "top"] = boxes.top.min()
        df.loc[boxes.index, "bottom"] = boxes.top.max()

    row = 0
    for t, boxes in df.groupby("top"):
        row += 1
        df.loc[boxes.index, "row"] = row

    df = df.sort_values(["row", "left"]).reset_index()
    return df


def arrange_rows_of_text(df: pd.DataFrame, gutter: int = 12) -> pd.DataFrame:
    """Move lines of text in a label closer together."""
    df["new_left"] = df.left
    df["new_top"] = df.top
    df["new_right"] = df.right
    df["new_bottom"] = df.bottom

    prev_bottom = gutter

    for row, boxes in df.groupby("row"):
        boxes = boxes.sort_values("left")

        height = boxes.bottom.max() - boxes.top.min()

        df.loc[boxes.index, "new_top"] = prev_bottom + gutter
        df.loc[boxes.index, "new_bottom"] = prev_bottom + height + gutter

        prev_bottom += height + gutter

        # prev_right = 0
        # margin = 0

        # for i, (idx, box) in enumerate(boxes.iterrows()):
        #     width = box.right - box.left

        #     if i == 0:
        #         prev_right = box.left
        #         margin = width // len(box.text)

        #     df.loc[idx, "new_left"] = prev_right + margin
        #     df.loc[idx, "new_right"] = prev_right + width + margin

        #     prev_right += width + margin

    return df
