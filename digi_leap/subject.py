"""A utility class to calulate average subject boxes."""

import json

import numpy as np

import digi_leap.util as util


class Subject:
    """A utility class to calulate average subject boxes."""

    def __init__(self):
        self.subject_id: str = ''
        self.subject_file_name: str = ''
        self.types: list[str] = np.array([], dtype=str)
        self.boxes: np.ndarray = np.empty((0, 4))
        self.groups: np.ndarray = np.array([])
        self.avg_boxes: list[np.ndarray] = []
        self.avg_types: list[str] = []

    def to_dict(self, *, everything=False) -> dict:
        """Convert this object to a dictionary."""
        as_dict = {
            'subject_id': self.subject_id,
            'subject_file_name': self.subject_file_name,
        }

        zippy = zip(self.avg_boxes, self.avg_types)
        for i, (box, type_) in enumerate(zippy, 1):
            as_dict[f'avg_box_{i}'] = self.bbox_to_json(box)
            as_dict[f'avg_type_{i}'] = type_

        if everything:
            zippy2 = zip(self.boxes, self.types, self.groups)
            for i, (box, type_, group) in enumerate(zippy2, 1):
                as_dict[f'box_{i}'] = self.bbox_to_json(box)
                as_dict[f'type_{i}'] = type_
                as_dict[f'group_{i}'] = group

        return as_dict

    @staticmethod
    def bbox_to_json(box: np.ndarray) -> dict[str, int]:
        """Convert a JSON box into a numpy array."""
        box = box.astype(int)
        as_dict: dict[str, int] = {
            'left': box[0],
            'top': box[1],
            'right': box[2],
            'bottom': box[3],
        }
        return as_dict

    @staticmethod
    def bbox_from_json(coords: str) -> np.ndarray:
        """Convert a JSON box into a numpy array."""
        temp = json.loads(coords)
        return np.array([temp['left'], temp['top'], temp['right'], temp['bottom']])

    def average_box_groups(self) -> None:
        """Average the box groups."""
        if len(self.boxes):
            self.groups = util.overlapping_boxes(self.boxes)
            self._sort_by_group()
            self._average_box_groups()

    def _sort_by_group(self) -> None:
        """Sort the boxes by box group."""
        idx = self.groups.argsort()
        self.boxes = self.boxes[idx]
        self.types = self.types[idx]
        self.groups = self.groups[idx]

    def _average_box_groups(self) -> None:
        """Compute the average box and type for each box group."""
        # Get average boxe per group
        wheres = np.where(self.groups[:-1] != self.groups[1:])[0] + 1
        box_groups = np.split(self.boxes, wheres)
        self.avg_boxes = [np.average(g, axis=0).round() for g in box_groups]

        # Select box type for average box
        type_groups = np.split(self.types, wheres)
        avg_types = [np.unique(g) for g in type_groups]
        self.avg_types = ['_'.join(sorted(t)) for t in avg_types]