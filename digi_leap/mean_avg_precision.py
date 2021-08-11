"""Calculate the mean average precision for scoring object detection results."""

import torch
from torchvision.ops import box_iou


def mAP_iou(results, low=0.5, high=0.95, step=0.05, eps=1e-8):
    """Calculate the mean average precision over several IoU thresholds."""
    high += step
    scores = [mAP(results, t, eps=eps) for t in torch.arange(low, high, step)]
    return sum(scores) / len(scores)


def mAP(results, iou_threshold=0.5, eps=1e-8):
    """Calculate the mean average precision at a specific IoU threshold.

    We're given a list of dictionaries with one dictionary per subject image.
    Each dict contains: (all values are torch tensors)
        image_id
        true_boxes = one row per box and each row is [x_min, y_min, x_max, y_max]
        true_labels = labels as integers
        pred_boxes = one row per box and each row is [x_min, y_min, x_max, y_max]
        pred_labels = labels as integers
        pred_scores = model confidence scores of each prediction
    """
    avg_precisions = []

    for result in results:
        true_count = len(result["true_labels"])
        pred_count = len(result["pred_labels"])

        iou = box_iou(result["true_boxes"], result["pred_boxes"])
        scores = result["pred_scores"].repeat(true_count, 1)

        for cls in set(result["true_labels"].tolist()):
            # Select all IoUs for the current class and is above the threshold
            mask = torch.zeros_like(iou, dtype=int)
            mask[result["true_labels"] == cls, :] = 1
            mask[:, result["pred_labels"] == cls] += 1
            mask = torch.bitwise_and(mask.eq(2), iou.ge(iou_threshold))

            # Get the max value for each row which is the true positive score
            masked_scores = scores.clone()
            masked_scores[~mask] = 0.0
            pred_max = torch.argmax(masked_scores, dim=1)

            tp = torch.zeros((pred_count,), dtype=int)
            tp[pred_max] = 1
            if masked_scores[:, 0].sum() == 0.0:
                tp[0] = 0

            # # Calculate the precision/recall curve
            tp_sum = torch.cumsum(tp, dim=0)
            n_pred = torch.arange(len(tp)) + 1

            precis = tp_sum / (n_pred + eps)
            recall = tp_sum / (true_count + eps)

            # Avg precision for this class
            avg_precisions.append(torch.trapz(precis, recall))

    return sum(avg_precisions) / (len(avg_precisions) + eps)
