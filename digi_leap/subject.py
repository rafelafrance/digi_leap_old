"""A utility class to calulate average subject boxes."""

import json

import numpy as np

import digi_leap.util as util


class Subject:
    """A utility class used to calulate merging subject boxes."""

    def __init__(self):
        self.subject_id: str = ''
        self.subject_file_name: str = ''
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
            'subject_id': self.subject_id,
            'subject_file_name': self.subject_file_name,
        }

        zippy = zip(self.merged_boxes, self.merged_types)
        for i, (box, type_) in enumerate(zippy, 1):
            as_dict[f'merged_box_{i}'] = self.bbox_to_json(box)
            as_dict[f'merged_type_{i}'] = type_

        if everything:
            zippy = zip(self.removed_boxes, self.removed_types)
            for i, (box, type_) in enumerate(zippy, 1):
                as_dict[f'removed_box_{i}'] = self.bbox_to_json(box)
                as_dict[f'removed_type_{i}'] = type_

            zippy2 = zip(self.boxes, self.types, self.groups)
            for i, (box, type_, group) in enumerate(zippy2, 1):
                as_dict[f'box_{i}'] = self.bbox_to_json(box)
                as_dict[f'type_{i}'] = type_
                as_dict[f'group_{i}'] = group

        return as_dict

    @staticmethod
    def bbox_to_json(box: np.ndarray) -> str:
        """Convert a JSON box into a numpy array."""
        as_dict: dict[str, int] = {
            'left': int(box[0]),
            'top': int(box[1]),
            'right': int(box[2]),
            'bottom': int(box[3]),
        }
        return json.dumps(as_dict)

    @staticmethod
    def bbox_from_json(coords: str) -> np.ndarray:
        """Convert a JSON box into a numpy array."""
        jj = json.loads(coords)
        return np.array([jj['left'], jj['top'], jj['right'], jj['bottom']])

    def merge_box_groups(self) -> None:
        """Merge box groups into a single bounding box per group."""
        if len(self.boxes) > 0:
            self._remove_multi_labels()
            self.groups = util.overlapping_boxes(self.boxes)
            self._sort_by_group()
            self._merge_boxes()

    def _remove_multi_labels(self):
        """Remove bounding boxes that contain multiple labels.

        Sometime people draw a bounding box around more than one label, this function
        tries to correct that by removing the outer bounding box and seeing if that
        breaks the remaining boxes into separate groups.
        """
        removes = np.array([], dtype=int)
        groups = util.find_box_groups(self.boxes, threshold=0.1)

        # Look for boxes that contain more than one label
        # Group all sub-boxes and count the subgroups
        # If the subgroup count > 1 then there are multiple labels
        max_group = np.max(groups)
        for g in range(1, max_group + 1):
            sub_boxes = self.boxes[groups == -g]
            subgroups = util.overlapping_boxes(sub_boxes)
            if len(subgroups) > 0 and subgroups.max() > 1:
                idx = np.argwhere(groups == g).flatten()
                removes = np.hstack((removes, idx))

        # Remove boxes that contain more than one label
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
        self.merged_types = ['_'.join(sorted(t)) for t in avg_types]
