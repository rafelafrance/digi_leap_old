"""A utility class to calculate average subject boxes."""

import json
from collections import namedtuple
from typing import Union

import numpy as np
import numpy.typing as npt

import digi_leap.box_calc as calc

ClipType = Union[list[int], tuple[int], None]

TYPE_CLASSES = {0: "None", 1: "Barcode", 2: "Both", 3: "Handwritten", 4: "Typewritten"}
TYPE = {v: k for k, v in TYPE_CLASSES.items()}

RECONCILE_TYPES = {
    "": TYPE["None"],
    "Barcode": TYPE["Barcode"],
    "Barcode_Both": TYPE["Barcode"],
    "Barcode_Both_Handwritten": TYPE["Barcode"],
    "Barcode_Both_Handwritten_Typewritten": TYPE["Barcode"],
    "Barcode_Both_Typewritten": TYPE["Barcode"],
    "Barcode_Handwritten": TYPE["Barcode"],
    "Barcode_Handwritten_Typewritten": TYPE["Barcode"],
    "Barcode_Typewritten": TYPE["Barcode"],
    "Both": TYPE["Both"],
    "Both_Handwritten": TYPE["Both"],
    "Both_Handwritten_Typewritten": TYPE["Both"],
    "Both_Typewritten": TYPE["Both"],
    "Handwritten": TYPE["Handwritten"],
    "Handwritten_Typewritten": TYPE["Both"],
    "Typewritten": TYPE["Typewritten"],
}

# Used for training data
SubjectTrainData = namedtuple("SubjectTrainData", "id path boxes labels")


# Used when merging bounding boxes
class Subject:
    """A utility class used to calculate merging subject boxes."""

    def __init__(self):
        self.subject_id: str = ""
        self.image_file: str = ""
        self.types: np.ndarray = np.array([], dtype=str)
        self.boxes: np.ndarray = np.empty((0, 4))
        self.groups: np.ndarray = np.array([])
        self.merged_boxes: list[np.ndarray] = []
        self.merged_types: list[str] = []
        self.removed_boxes: np.ndarray = np.empty((0, 4))
        self.removed_types: np.ndarray = np.array([], dtype=str)

    def to_dict(self, *, everything=False) -> dict:
        """Convert this object to a dictionary."""
        as_dict = {
            "subject_id": self.subject_id,
            "image_file": self.image_file,
        }

        zippy = zip(self.merged_boxes, self.merged_types)
        for i, (box, type_) in enumerate(zippy, 1):
            as_dict[f"merged_box_{i}"] = self.bbox_to_json(box)
            as_dict[f"merged_type_{i}"] = type_

        if everything:
            zippy = zip(self.removed_boxes, self.removed_types)
            for i, (box, type_) in enumerate(zippy, 1):
                as_dict[f"removed_box_{i}"] = self.bbox_to_json(box)
                as_dict[f"removed_type_{i}"] = type_

            zippy2 = zip(self.boxes, self.types, self.groups)
            for i, (box, type_, group) in enumerate(zippy2, 1):
                as_dict[f"box_{i}"] = self.bbox_to_json(box)
                as_dict[f"type_{i}"] = type_
                as_dict[f"group_{i}"] = group

        return as_dict

    @staticmethod
    def bbox_to_json(box: np.ndarray) -> str:
        """Convert a JSON box into a numpy array."""
        as_dict: dict[str, int] = {
            "left": int(box[0]),
            "top": int(box[1]),
            "right": int(box[2]),
            "bottom": int(box[3]),
        }
        return json.dumps(as_dict)

    @staticmethod
    def bbox_from_json(coords: str, clip: ClipType = None) -> npt.ArrayLike:
        """Convert a JSON box into a numpy array."""
        jj = json.loads(coords)
        box = np.array([jj["left"], jj["top"], jj["right"], jj["bottom"]])
        if clip:
            box[[0, 2]] = np.clip(box[[0, 2]], 0, clip[0])
            box[[1, 3]] = np.clip(box[[1, 3]], 0, clip[1])
        return box

    def merge_box_groups(self) -> None:
        """Merge box groups into a single bounding box per group."""
        if len(self.boxes) > 0:
            self._remove_multi_labels()
            self._remove_unlabeled()
            self.groups = calc.overlapping_boxes(self.boxes)
            self._sort_by_group()
            self._merge_boxes()

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
        self.merged_boxes = [np.hstack((mn[:2], mx[2:])) for mn, mx in zip(mins, maxs)]
        # self.merged_boxes = [np.mean(g, axis=0).round() for g in box_groups]

        # Select box type for the merged box
        type_groups = np.split(self.types, wheres)
        avg_types = [np.unique(g) for g in type_groups]
        self.merged_types = ["_".join(sorted(t)) for t in avg_types]
