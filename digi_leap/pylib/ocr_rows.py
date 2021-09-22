"""Find rows of text in the OCR output.

It takes a dataframe of the OCR output and returns a sorted dataframe with
row order and each row in left-to-right order. I call the algorithm "Marching
Center lines" because it is looking at the center lines (horizontal) of text
bounding boxes as they progress across the label.
"""

from dataclasses import dataclass, field
from typing import Union

import pandas as pd


@dataclass
class Row:
    """Holds data for building a row."""

    left: int
    top: int
    right: int
    bottom: int
    row_id: int = 0

    @property
    def center(self) -> int:
        """Get the vertical center line of the box."""
        return (self.bottom + self.top) // 2

    @property
    def width(self) -> int:
        """Get the width of the box."""
        return self.right - self.left + 1

    def update(self, left, top, right, bottom) -> None:
        """Update the row with the last box coordinates."""
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom


@dataclass
class Rows:
    """A row container."""

    row_id: int = 0
    rows: list[Row] = field(default_factory=list)

    def __iter__(self) -> iter:
        return iter(self.rows)

    def new_row(self, row) -> Row:
        """Add a row to the list."""
        self.row_id += 1
        row.row_id = self.row_id
        self.rows.append(row)
        return row

    def overlapping_rows(self, box: pd.Series) -> Union[Row, None]:
        """Get the rows that overlap (vertically) with the given box.

        I'm defining an overlap as a box's top and bottom covering a row's center
        line. If a tall box overlaps with multiple row center lines then I want
        the row with the center line closest to the given box's center line.
        """
        overlap = [r for r in self.rows if box.top <= r.center <= box.bottom]

        if len(overlap) > 1:
            mid = (box.top + box.bottom) // 2
            overlap = sorted(overlap, key=lambda rb: abs(rb.center - mid))

        return overlap[0] if overlap else None

    def row_brackets_box(self, box: pd.Series) -> Union[Row, None]:
        """Check if the given box is fully contained within a row.

        A tiny box may not overlap a center line but still be contained entirely
        within a row. This happens for very small boxes, typically punctuation.
        """
        contains = [r for r in self.rows if r.top <= box.top and r.bottom >= box.bottom]
        return contains[0] if contains else None


def horizontal_overlap(box, row):
    """Calculate how much boxes overlap horizontally.

    Boxes on the same row will often overlap. I will use this value to see if I want
    to create a new row. This is calculating the fraction of overlap of the thinner
    box.
    """
    max_left = max(box.left, row.left)
    min_right = min(box.right, row.right)
    min_width = min(box.width, row.width)
    horiz_overlap = (min_right - max_left) / min_width
    return horiz_overlap


def find_rows_of_text(df: pd.DataFrame, width_threshold: float = 0.5) -> pd.DataFrame:
    """Find rows of text in the label and mark what row each box belongs to.

    Lines of text may curve or slant up or downwards so finding rows of text is not as
    straightforward as sorting bounding boxes. The general idea is to compare the
    current box's top and bottom and see if it brackets the vertical center line of
    the last box in and existing row.
    1) Put all bounding boxes in left-to-right order.
    2) For each bounding box:
        a) If the bounding box is bracketed by the last box in the row then it gets
           appended to the row. This often happens with punctuation.
        b) If the bounding box overlaps a row's last box's center line and there is
           no significant horizontal overlap then then append the box to the row.
        c) If a & b fail then create a new row.
    3) Put the rows in top to bottom order and then each row into left to right order.
    """
    df = df.sort_values(["left", "top"])
    df["width"] = df["right"] - df["left"] + 1

    rows = Rows()

    for idx, box in df.iterrows():
        if row := rows.row_brackets_box(box):
            row.update(box.left, box.top, box.right, box.bottom)
        else:
            row = rows.overlapping_rows(box)
            if row and horizontal_overlap(box, row) < width_threshold:
                row.update(box.left, box.top, box.right, box.bottom)
            else:
                row = rows.new_row(Row(box.left, box.top, box.right, box.bottom))

        df.at[idx, "row"] = row.row_id

    rows = sorted(rows, key=lambda r: r.top)
    order = {r.row_id: i for i, r in enumerate(rows)}

    df["row"] = df.row.map(order)
    df = df.sort_values(["row", "left"])

    return df
