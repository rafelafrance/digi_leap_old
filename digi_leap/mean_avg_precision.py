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

    Loosely based off of:
    https://github.com/eriklindernoren/PyTorch-YOLOv3/blob/master/pytorchyolo
    /utils/utils.py

    We're given a list of dictionaries with one dictionary per subject image.
    Each dict contains: (all values are torch tensors)
        image_id
        true_boxes = one row per box and each row is [x_min, y_min, x_max, y_max]
        true_labels = labels as integers
        pred_boxes = one row per box and each row is [x_min, y_min, x_max, y_max]
        pred_labels = labels as integers
        pred_scores = model confidence scores of each prediction
    """
    all_ap = []

    for result in results:
        iou = box_iou(result["true_boxes"], result["pred_boxes"])

        for cls in result["true_labels"].unique():
            # Limit scores and IoUs to this class
            class_scores = result["pred_scores"][result["pred_labels"] == cls]

            class_iou = iou[result["true_labels"] == cls, :]
            class_iou = class_iou[:, result["pred_labels"] == cls]

            # Order true positives by scores
            order = class_scores.argsort(descending=True)

            # Find true positives
            is_tp = torch.zeros(class_iou.shape[1])
            for col in order:
                max_iou, row = class_iou[:, col].max(dim=0)
                if max_iou >= iou_threshold:
                    is_tp[col] = 1.0
                    class_iou[:, col] = 0.0
                    class_iou[row, :] = 0.0
            is_tp = is_tp[order]

            # Calculate precision and recall
            tp_cumsum = is_tp.cumsum(dim=0)
            fp_cumsum = (1.0 - is_tp).cumsum(dim=0)
            n_ground_truth = class_iou.shape[0]

            pre = tp_cumsum / (tp_cumsum + fp_cumsum + eps)
            rec = tp_cumsum / (n_ground_truth + eps)

            # Build the precision/recall curve
            pre = torch.cat((torch.tensor([0.0]), pre, torch.tensor([0.0])))
            rec = torch.cat((torch.tensor([0.0]), rec, torch.tensor([1.0])))

            # Remove precision/recall curve jaggies
            for i in range(pre.shape[0] - 1, 0, -1):
                pre[i - 1] = torch.maximum(pre[i - 1], pre[i])

            # Calculate the AUC
            idx = torch.where(rec[1:] != rec[:-1])[0]
            ap = torch.sum((rec[idx + 1] - rec[idx]) * pre[idx + 1])

            all_ap.append(ap)

    return sum(all_ap) / (len(all_ap) + eps)
