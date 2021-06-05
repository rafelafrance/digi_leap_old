"""Test functions in subject.py."""

import unittest

import numpy as np
import numpy.testing as npt

from digi_leap.subject import Subject


class TestSubject(unittest.TestCase):
    """Test functions in subject.py."""

    def test_remove_multi_labels_01(self):
        """It removes a box with multiple labels."""
        subject = Subject()
        boxes = np.array([
            [0, 0, 100, 100],
            [5, 5, 90, 45],
            [5, 55, 90, 95],
        ])
        types = np.array(['a', 'a', 'a'], dtype=str)
        subject.types = types
        subject.boxes = boxes
        subject._remove_multi_labels()

        npt.assert_array_equal(subject.boxes, boxes[1:])
        npt.assert_array_equal(subject.types, types[1:])
        npt.assert_array_equal(subject.removed_boxes, boxes[:1])
        npt.assert_array_equal(subject.removed_types, types[:1])

    def test_remove_multi_labels_02(self):
        """It removes a box with multiple labels."""
        subject = Subject()
        boxes = np.array([
            [1863, 3218, 2735, 4093],
            [1854, 3272, 2602, 3508],
            [1902, 3531, 2666, 4063],
            [1893, 3271, 2714, 4089],
            [98, 3862, 599, 4097],
            [124, 3920, 517, 4065],
            [106, 3893, 579, 4095],
        ])
        types = np.array(['a'] * 7, dtype=str)
        subject.types = types
        subject.boxes = boxes
        subject._remove_multi_labels()

        npt.assert_array_equal(subject.boxes, boxes[1:])
        npt.assert_array_equal(subject.types, types[1:])
        npt.assert_array_equal(subject.removed_boxes, boxes[:1])
        npt.assert_array_equal(subject.removed_types, types[:1])

