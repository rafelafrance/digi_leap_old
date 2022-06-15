"""Test the mean average precision."""
import unittest

import torch

from digi_leap.pylib.mean_avg_precision import map_
from digi_leap.pylib.mean_avg_precision import map_iou


class TestMeanAvgPrecision(unittest.TestCase):
    """Test the mean average precision."""

    def test_map_01(self):
        """It handles boxes being equal."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]],
                ),
                "true_labels": torch.Tensor([1, 2]),
                "pred_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]],
                ),
                "pred_labels": torch.Tensor([1, 2]),
                "pred_scores": torch.Tensor([0.8, 0.9]),
            },
        ]
        self.assertEqual(map_(results), 1.0)

    def test_map_02(self):
        """It handles non-overlapping boxes."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[0, 0, 1000, 1000], [1000, 1000, 2000, 2000]],
                ),
                "true_labels": torch.Tensor([1, 1]),
                "pred_boxes": torch.Tensor(
                    [
                        [2000, 2000, 3000, 3000],
                        [100, 0, 1000, 1000],
                        [5000, 5000, 6000, 6000],
                    ]
                ),
                "pred_labels": torch.Tensor([1, 1, 1]),
                "pred_scores": torch.Tensor([0.7, 0.8, 0.9]),
            },
        ]
        self.assertAlmostEqual(map_(results).item(), 0.25)

    def test_map_03(self):
        """It handles boxes, labels, & scores being equal."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]],
                ),
                "true_labels": torch.Tensor([1, 1]),
                "pred_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]],
                ),
                "pred_labels": torch.Tensor([1, 1]),
                "pred_scores": torch.Tensor([0.8, 0.8]),
            },
        ]
        self.assertEqual(map_(results), 1.0)

    def test_map_04(self):
        """It handles classes being unequal."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]],
                ),
                "true_labels": torch.Tensor([1, 1]),
                "pred_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]],
                ),
                "pred_labels": torch.Tensor([2, 2]),
                "pred_scores": torch.Tensor([0.8, 0.8]),
            },
        ]
        self.assertEqual(map_(results), 0.0)

    def test_map_05(self):
        """It handles false negatives."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]],
                ),
                "true_labels": torch.Tensor([1, 1]),
                "pred_boxes": torch.Tensor([[100, 100, 800, 800]]),
                "pred_labels": torch.Tensor([1]),
                "pred_scores": torch.Tensor([1.0]),
            },
        ]
        self.assertEqual(map_(results), 0.5)

    def test_map_06(self):
        """It handles multiple samples."""
        results = [
            # Both empty: 1.0
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.empty((0, 4), dtype=torch.float32),
                "true_labels": torch.Tensor([]),
                "pred_boxes": torch.empty((0, 4), dtype=torch.float32),
                "pred_labels": torch.Tensor([]),
                "pred_scores": torch.Tensor([]),
            },
            # True empty: 0.0
            {
                "image_id": torch.Tensor([2]),
                "true_boxes": torch.empty((0, 4), dtype=torch.float32),
                "true_labels": torch.Tensor([]),
                "pred_boxes": torch.Tensor([[100, 100, 800, 800]]),
                "pred_labels": torch.Tensor([1]),
                "pred_scores": torch.Tensor([1.0]),
            },
            # Predicted empty: 0.0
            {
                "image_id": torch.Tensor([4]),
                "true_boxes": torch.Tensor([[100, 100, 800, 800]]),
                "true_labels": torch.Tensor([1]),
                "pred_boxes": torch.empty((0, 4), dtype=torch.float32),
                "pred_labels": torch.Tensor([]),
                "pred_scores": torch.Tensor([]),
            },
            # Identical: 1.0
            {
                "image_id": torch.Tensor([3]),
                "true_boxes": torch.Tensor([[100, 100, 800, 800]]),
                "true_labels": torch.Tensor([1]),
                "pred_boxes": torch.Tensor([[100, 100, 800, 800]]),
                "pred_labels": torch.Tensor([1]),
                "pred_scores": torch.Tensor([0.8]),
            },
        ]
        self.assertAlmostEqual(map_(results).item(), 0.5)

    def test_map_iou_01(self):
        """It averages the various thresholds."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [
                        [0, 0, 10, 10],
                        [10, 10, 20, 20],
                        [20, 20, 30, 30],
                        [30, 30, 40, 40],
                        [40, 40, 50, 50],
                        [50, 50, 60, 60],
                    ],
                ),
                "true_labels": torch.Tensor([1, 2, 3, 1, 2, 3]),
                "pred_boxes": torch.Tensor(
                    [
                        [0, 0, 5, 10],
                        [10, 10, 16, 20],
                        [20, 20, 27, 30],
                        [30, 30, 38, 40],
                        [40, 40, 49, 50],
                        [50, 50, 60, 60],
                    ],
                ),
                "pred_labels": torch.Tensor([1, 2, 3, 1, 2, 3]),
                "pred_scores": torch.Tensor([0.8, 0.9, 0.6, 0.8, 0.9, 0.6]),
            },
        ]
        self.assertEqual(map_(results, iou_threshold=0.5), 1.0)
        self.assertEqual(map_(results, iou_threshold=0.6), 0.75)
        self.assertEqual(map_(results, iou_threshold=0.7), 0.5)
        self.assertEqual(map_(results, iou_threshold=0.8), 0.25)
        self.assertAlmostEqual(
            map_iou(results, low=0.5, high=0.8, step=0.1).item(), 0.625
        )
