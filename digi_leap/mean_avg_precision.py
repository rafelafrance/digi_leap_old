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
    all_ap = []

    for result in results:
        iou = box_iou(result["true_boxes"], result["pred_boxes"])

        for cls in set(result["true_labels"].tolist()):
            class_scores = result["pred_scores"][result["pred_labels"] == cls]

            class_iou = iou[result["true_labels"] == cls, :]
            class_iou = class_iou[:, result["pred_labels"] == cls]

            order = class_scores.argsort(descending=True)

            is_tp = torch.zeros(class_scores.shape[0])
            for col in order:
                max_iou, row = class_iou[:, col].max(dim=0)
                if max_iou >= iou_threshold:
                    is_tp[col] = 1
                    class_iou[:, col] = 0.0
                    class_iou[row, :] = 0.0

            is_tp = is_tp[order]

            cumsum = is_tp.cumsum(dim=0)
            rank = torch.arange(is_tp.shape[0]) + 1

            pre = cumsum / (rank + eps)
            rec = cumsum / (cumsum.shape[0] + eps)

            pre = torch.cat((torch.tensor([0.0]), pre, torch.tensor([pre[-1]])))
            rec = torch.cat((torch.tensor([0.0]), rec, torch.tensor([1.0])))

            pre = pre.flip(dims=(0,))  # flip() is slower than reshape()
            pre, _ = pre.cummax(dim=0)
            pre = pre.flip(dims=(0,))

            ap = torch.trapz(pre, rec)
            all_ap.append(ap)

    return sum(all_ap) / (len(all_ap) + eps)
