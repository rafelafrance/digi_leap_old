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
        iou = box_iou(result["true_boxes"], result["pred_boxes"])
        scores = result["pred_scores"].repeat(len(result["true_labels"]), 1)
        scores[iou.lt(iou_threshold)] = 0.0

        for cls in set(result["true_labels"].tolist()):
            # Select all scores for the current class
            class_scores = scores[result["true_labels"] == cls, :]
            class_scores = class_scores[:, result["pred_labels"] == cls]

            if class_scores.shape[1] == 0:
                avg_precisions.append(0.0)
                continue

            # Find the true positives
            conf, _ = torch.max(class_scores, dim=0)
            tp_idx = torch.argmax(class_scores, dim=1)
            tp = torch.zeros(class_scores.shape[1])
            tp[tp_idx] = 1

            order = (-conf).argsort()
            tp = tp[order]
            conf = conf[order]

            # Calculate the precision/recall curve
            tp_sum = torch.cumsum(tp, dim=0)
            n_pred = torch.arange(tp.shape[0]) + 1

            precis = tp_sum / (n_pred + eps)
            precis = torch.cat((torch.tensor([1]), precis))

            recall = tp_sum / (tp.shape[0] + eps)
            recall = torch.cat((torch.tensor([0]), recall))

            # Avg precision for this class
            avg_precisions.append(torch.trapz(precis, recall))

    return sum(avg_precisions) / (len(avg_precisions) + eps)
