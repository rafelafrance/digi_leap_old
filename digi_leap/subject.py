"""A utility class to calculate average subject boxes."""

import json
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

import digi_leap.box_calc as calc

CLASSES = "None Barcode Both Handwritten Typewritten".split()
CLASS2INT = {c: i for i, c in enumerate(CLASSES, 1)}
CLASS2NAME = {v: k for k, v in CLASS2INT.items()}

RECONCILE_TYPES = {
    tuple(): "None",
    ("Barcode",): "Barcode",
    ("Barcode", "Both"): "Barcode",
    ("Barcode", "Both", "Handwritten"): "Barcode",
    ("Barcode", "Both", "Handwritten", "Typewritten"): "Barcode",
    ("Barcode", "Both", "Typewritten"): "Barcode",
    ("Barcode", "Handwritten"): "Barcode",
    ("Barcode", "Handwritten", "Typewritten"): "Barcode",
    ("Barcode", "Typewritten"): "Barcode",
    ("Both",): "Both",
    ("Both", "Handwritten"): "Both",
    ("Both", "Handwritten", "Typewritten"): "Both",
    ("Both", "Typewritten"): "Both",
    ("Handwritten",): "Handwritten",
    ("Handwritten", "Typewritten"): "Both",
    ("Typewritten",): "Typewritten",
}


# Used when merging bounding boxes
@dataclass
class Subject:
    """A utility class used to calculate merging subject boxes."""

    subject_id: str = ""
    image_file: str = ""
    image_size: tuple[int, int] = field(default_factory=tuple)
    groups: np.ndarray = field(default_factory=lambda: np.array([]))
    boxes: np.ndarray = field(default_factory=lambda: np.empty((0, 4), dtype=np.int32))
    types: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    merged_boxes: np.ndarray = field(
        default_factory=lambda: np.empty((0, 4), dtype=np.int32)
    )
    merged_types: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))
    removed_boxes: np.ndarray = field(
        default_factory=lambda: np.empty((0, 4), dtype=np.int32)
    )
    removed_types: np.ndarray = field(default_factory=lambda: np.array([], dtype=str))

    def to_dict(self):
        """Custom asdict."""
        return {
            "subject_id": self.subject_id,
            "image_file": self.image_file,
            "image_size": list(self.image_size),
            "groups": self.groups.tolist(),
            "boxes": self.boxes.tolist(),
            "types": self.types.tolist(),
            "removed_boxes": self.removed_boxes.tolist(),
            "removed_types": self.removed_types.tolist(),
            "merged_boxes": list(self.merged_boxes),
            "merged_types": list(self.merged_types),
        }

    @staticmethod
    def bbox_from_json(coords: str) -> npt.ArrayLike:
        """Convert a JSON box into a numpy array."""
        jj = json.loads(coords)
        box = np.array([jj["left"], jj["top"], jj["right"], jj["bottom"]])
        return box

    def merge_box_groups(self) -> None:
        """Merge box groups into a single bounding box per group."""
        if len(self.boxes) > 0:
            self._remove_multi_labels()
            self._remove_unlabeled()
            self.groups = calc.overlapping_boxes(self.boxes)
            self._sort_by_group()
            self._merge_boxes()
            self._filter_merged_boxes()

    def _remove_unlabeled(self):
        """Remove solo boxes that have no labels.

        Sometimes people draw a box around the wrong thing like a plant part or an
        empty part of the sheet etc. This function tries to remove those boxes. It is
        unlikely that two people will do the same random box and it is also unlikely
        (I hope) that the box will be given a box type.
        """
        removes = np.array([], dtype=int)
        groups = calc.overlapping_boxes(self.boxes, threshold=0.1)
        max_group = np.max(groups)
        for g in range(1, max_group + 1):
            group = self.boxes[groups == g]
            types = self.types[groups == g]
            if len(group) == 1 and not types[0]:
                idx = np.argwhere(groups == g).flatten()
                removes = np.hstack((removes, idx))

        self._remove_boxes(groups, removes)

    def _remove_multi_labels(self):
        """Remove bounding boxes that contain multiple labels.

        Sometimes people draw a bounding box around more than one label, this function
        tries to correct that by removing the outer bounding box and seeing if that
        breaks the remaining boxes into separate groups.
        """
        removes = np.array([], dtype=int)
        groups = calc.find_box_groups(self.boxes, threshold=0.1)

        # Look for boxes that contain more than one label
        # Group all sub-boxes and count the subgroups
        # If the subgroup count > 1 then there are multiple labels
        max_group = np.max(groups)
        for g in range(1, max_group + 1):
            sub_boxes = self.boxes[groups == -g]
            subgroups = calc.overlapping_boxes(sub_boxes)
            if len(subgroups) > 0 and subgroups.max() > 1:
                idx = np.argwhere(groups == g).flatten()
                removes = np.hstack((removes, idx))

        self._remove_boxes(groups, removes)

    def _remove_boxes(self, groups, removes):
        """Remove boxes."""
        if len(removes) > 0:
            mask = np.zeros_like(groups, dtype=bool)
            mask[removes] = True
            self.removed_boxes = self.boxes[mask]
            self.removed_types = self.types[mask]
            self.boxes = self.boxes[~mask]
            self.types = self.types[~mask]

    def _sort_by_group(self) -> None:
        """Sort the boxes by box group."""
        idx = self.groups.argsort()
        self.boxes = self.boxes[idx]
        self.types = self.types[idx]
        self.groups = self.groups[idx]

    def _merge_boxes(self) -> None:
        """Compute the merged box and type for each box group."""
        # Get maximum box per group
        wheres = np.where(self.groups[:-1] != self.groups[1:])[0] + 1
        box_groups = np.split(self.boxes, wheres)

        mins = [np.min(g, axis=0).round() for g in box_groups]
        maxs = [np.max(g, axis=0).round() for g in box_groups]
        self.merged_boxes = [
            np.hstack((mn[:2], mx[2:])).tolist() for mn, mx in zip(mins, maxs)
        ]
        # self.merged_boxes = [np.mean(g, axis=0).round() for g in box_groups]

        # Select box type for the merged box
        type_groups = np.split(self.types, wheres)
        avg_types = [sorted(np.unique(g)) for g in type_groups]
        avg_types = [t if t[0] else t[1:] for t in avg_types]
        self.merged_types = np.array([RECONCILE_TYPES[tuple(t)] for t in avg_types])

    def _filter_merged_boxes(self, threshold: int = 12) -> None:
        """Remove degenerate merged boxes."""
        boxes, types = [], []
        for box, type_ in zip(self.merged_boxes, self.merged_types):
            if box[2] - box[0] >= threshold and box[3] - box[1] >= threshold:
                boxes.append(box)
                types.append(type_)
        self.merged_boxes = boxes
        self.merged_types = types
