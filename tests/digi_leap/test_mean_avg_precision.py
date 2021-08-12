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
        """It handles non-overlapping boxes."""
        results = [
            {
                "image_id": torch.Tensor([1]),
                "true_boxes": torch.Tensor(
                    [[0, 0, 1000, 1000], [1000, 1000, 2000, 2000]]
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
        self.assertAlmostEqual(mAP(results).item(), 0.3889, 4)

    def test_mAP_03(self):
        """It handles boxes, labels, & scores being equal."""
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
                "pred_scores": torch.Tensor([0.8, 0.8]),
            },
        ]
        self.assertEqual(mAP(results), 1.0)

    def test_mAP_04(self):
        """It handles classes being unequal."""
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
                "pred_scores": torch.Tensor([0.8, 0.8]),
            },
        ]
        self.assertEqual(mAP(results), 0.0)
