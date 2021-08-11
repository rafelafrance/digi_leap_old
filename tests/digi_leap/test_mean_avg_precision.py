"""Test the mean average precision."""

import unittest

import torch

from digi_leap.mean_avg_precision import mAP


class TestMeanAvgPrecision(unittest.TestCase):
    """Test the mean average precision."""

    def test_mAP_01(self):
        """It handles boxes being equal."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]]
                ),
                "true_labels": torch.Tensor([1, 2]),
                "pred_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]]
                ),
                "pred_labels": torch.Tensor([1, 2]),
                "pred_scores": torch.Tensor([0.8, 0.9]),
            },
        ]
        self.assertEqual(mAP(results), 1.0)

    def test_mAP_02(self):
        """It handles boxes, classes, and scores are equal."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]]
                ),
                "true_labels": torch.Tensor([1, 1]),
                "pred_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]]
                ),
                "pred_labels": torch.Tensor([1, 1]),
                "pred_scores": torch.Tensor([0.9, 0.9]),
            },
        ]
        self.assertEqual(mAP(results), 1.0)

    def test_mAP_03(self):
        """It handles boxes, classes, and scores are equal."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]]
                ),
                "true_labels": torch.Tensor([1, 2]),
                "pred_boxes": torch.Tensor(
                    [
                        [100, 100, 800, 800],
                        [1000, 1000, 2000, 2000],
                        [110, 110, 900, 900],
                    ]
                ),
                "pred_labels": torch.Tensor([1, 2, 1]),
                "pred_scores": torch.Tensor([0.7, 0.8, 0.9]),
            },
        ]
        self.assertEqual(mAP(results), 0.75)

    def test_mAP_04(self):
        """It handles boxes, classes, and scores are equal."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[1000, 0, 2000, 500], [2000, 0, 3000, 500]]
                ),
                "true_labels": torch.Tensor([1, 2]),
                "pred_boxes": torch.Tensor(
                    [
                        [500, 0, 1500, 500],
                        [1500, 0, 2500, 500],
                        [1500, 0, 2500, 500],
                    ]
                ),
                "pred_labels": torch.Tensor([1, 1, 2]),
                "pred_scores": torch.Tensor([0.7, 0.8, 0.9]),
            },
        ]
        self.assertEqual(mAP(results, iou_threshold=0.3), 0.75)

    def test_mAP_05(self):
        """It handles boxes being equal but with differrent classes."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]]
                ),
                "true_labels": torch.Tensor([1, 1]),
                "pred_boxes": torch.Tensor(
                    [[100, 100, 800, 800], [1000, 1000, 2000, 2000]]
                ),
                "pred_labels": torch.Tensor([2, 2]),
                "pred_scores": torch.Tensor([0.8, 0.9]),
            },
        ]
        self.assertEqual(mAP(results), 0.0)
