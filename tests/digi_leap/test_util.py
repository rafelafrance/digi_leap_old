"""Test utilities."""

import unittest

import numpy as np
import numpy.testing as npt

import digi_leap.util as util


class TestUtil(unittest.TestCase):
    """Test functions in util.oy."""

    def test_iou_01(self):
        """It handles disjoint boxes."""
        box1 = [10, 10, 20, 20]
        box2 = [30, 30, 40, 40]
        self.assertEqual(util.iou(box1, box2), 0.0)

    def test_iou_02(self):
        """It handles disjoint boxes."""
        box1 = [30, 30, 40, 40]
        box2 = [10, 10, 20, 20]
        self.assertEqual(util.iou(box1, box2), 0.0)

    def test_iou_03(self):
        """It handles one box inside of another box."""
        box1 = [0, 0, 10, 10]
        box2 = [0, 0, 5, 5]
        i1 = 11.0 * 11.0
        i2 = 6.0 * 6.0
        self.assertEqual(util.iou(box1, box2), (i2 / (i1 + i2 - i2)))

    def test_nms_01(self):
        """It handles non-overlapping."""
        boxes = np.array([
            [10, 10, 20, 20],
            [30, 30, 40, 40],
            [50, 50, 60, 60],
        ])
        npt.assert_array_equal(util.nms(boxes), boxes)

    def test_nms_02(self):
        """It handles one box inside another."""
        boxes = np.array([
            [100, 100, 400, 400],
            [110, 110, 390, 390],
        ])
        npt.assert_array_equal(util.nms(boxes), [boxes[0]])

    def test_nms_03(self):
        """It handles overlap above the threshold."""
        boxes = np.array([
            [100, 100, 400, 400],
            [110, 110, 410, 410],
        ])
        npt.assert_array_equal(util.nms(boxes), [boxes[1]])

    def test_nms_04(self):
        """It handles overlap below the threshold."""
        boxes = np.array([
            [100, 100, 400, 400],
            [399, 399, 500, 500],
        ])
        npt.assert_array_equal(util.nms(boxes), boxes[::-1, :])
