"""Train a model to recognize labels on herbarium sheets."""
import logging

import torch
import torchvision
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import batched_nms

from digi_leap.pylib import box_calc as calc
from digi_leap.pylib import label_finder_data as data
from digi_leap.pylib import mean_avg_precision as mAP
from digi_leap.pylib import subject as sub
from digi_leap.pylib import util


def train(args):
    """Train the neural net."""
    torch.multiprocessing.set_sharing_strategy("file_system")

    state = torch.load(args.prev_model) if args.prev_model else {}

    model = get_model()
    if state.get("model_state"):
        model.load_state_dict(state["model_state"])

    device = torch.device(args.device)
    model.to(device)

    params = [p for p in model.parameters() if p.requires_grad]

    optimizer = torch.optim.SGD(
        params, lr=args.learning_rate, momentum=0.9, weight_decay=0.0005
    )
    if state.get("optimizer_state"):
        optimizer.load_state_dict(state["optimizer_state"])

    train_dataset, valid_dataset = get_subjects(
        args.reconciled_jsonl, args.sheets_dir, args.split, args.limit
    )
    train_loader = get_loader(train_dataset, args.batch_size, args.workers, True)
    valid_loader = get_loader(valid_dataset, args.batch_size, args.workers)

    start_epoch = state["epoch"] + 1 if state.get("epoch") else 1
    end_epoch = start_epoch + args.epochs + 1

    best_score = state["best_score"] if state.get("best_score") else -1.0
    best_loss = state["best_loss"] if state.get("best_loss") else 99999.0

    for epoch in range(start_epoch, end_epoch):
        train_loss = train_epoch(model, train_loader, device, optimizer)

        score = score_epoch(
            model, valid_loader, device, args.nms_threshold, args.sbs_threshold
        )

        log_results(epoch, train_loss, best_loss, score, best_score)

        best_loss, best_score = save_state(
            model,
            optimizer,
            epoch,
            train_loss,
            best_loss,
            score,
            best_score,
            args.curr_model,
        )


def test(args):
    """Train the neural net."""
    torch.multiprocessing.set_sharing_strategy("file_system")

    state = torch.load(args.curr_model)

    model = get_model()
    model.load_state_dict(state["model_state"])

    device = torch.device(args.device)
    model.to(device)

    _, dataset = get_subjects(args.reconciled_jsonl, args.sheets_dir, 1.0, args.limit)
    loader = get_loader(dataset, args.batch_size, args.workers)

    test_score = state["best_score"] if state.get("best_score") else -1.0

    score = score_epoch(model, loader, device, args.nms_threshold, args.sbs_threshold)

    logging.info(f"Train mAP: {test_score:0.3f}, test mAP: {score:0.3f}")


def get_subjects(reconciled_jsonl, sheets_dir, split, limit):
    """Get the subjects."""
    subjects = data.FasterRcnnData.read_jsonl(reconciled_jsonl)

    if limit:
        subjects = subjects[:limit]

    train_subjects, valid_subjects = train_test_split(subjects, test_size=split)
    train_dataset = data.FasterRcnnData(train_subjects, sheets_dir, augment=True)
    valid_dataset = data.FasterRcnnData(valid_subjects, sheets_dir)
    return train_dataset, valid_dataset


def get_loader(dataset, batch_size, workers, shuffle=False):
    """Get the data loaders."""
    return DataLoader(
        dataset,
        shuffle=shuffle,
        batch_size=batch_size,
        num_workers=workers,
        collate_fn=util.collate_fn,
    )


def train_epoch(model, loader, device, optimizer):
    """Train for one epoch."""
    model.train()

    running_loss = 0.0
    count = 0

    for images, targets in loader:
        count += len(targets)

        images = list(image.to(device) for image in images)
        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())
        loss_value = losses.item()
        running_loss += loss_value

        optimizer.zero_grad()
        losses.backward()
        optimizer.step()

    return running_loss / count


def score_epoch(model, loader, device, nms_threshold, sbs_threshold):
    """Evaluate the model."""
    model.eval()

    all_results = []

    for images, targets in loader:
        images = list(image.to(device) for image in images)

        with torch.no_grad():
            preds = model(images)

        for pred, target in zip(preds, targets):
            boxes = pred["boxes"].detach().cpu()
            labels = pred["labels"].detach().cpu()
            scores = pred["scores"].detach().cpu()

            idx = batched_nms(boxes, scores, labels, nms_threshold)
            boxes = boxes[idx, :]
            labels = labels[idx]
            scores = scores[idx]

            idx = calc.small_box_suppression(boxes, sbs_threshold)
            all_results.append(
                {
                    "image_id": target["image_id"],
                    "true_boxes": target["boxes"],
                    "true_labels": target["labels"],
                    "pred_boxes": boxes[idx, :],
                    "pred_labels": labels[idx],
                    "pred_scores": scores[idx],
                }
            )

    score = mAP.mAP_iou(all_results)
    return score


def log_results(epoch, train_loss, best_loss, score, best_score):
    """Print results to screen."""
    new_score = "*" if score > best_score else ""
    new_loss = "*" if train_loss < best_loss else " "
    logging.info(
        f"Epoch {epoch} Train loss: {train_loss:0.3f} {new_loss}, "
        f"mAP: {score:0.3f} {new_score}"
    )


def save_state(
    model, optimizer, epoch, train_loss, best_loss, score, best_score, save_model
):
    """Save the current model if it scores well."""
    best_loss = train_loss if train_loss < best_loss else best_loss

    if score > best_score:
        torch.save(
            {
                "epoch": epoch,
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "best_score": score,
                "best_loss": best_loss,
            },
            save_model,
        )
        return best_loss, score

    return best_loss, best_score


def get_model():
    """Get the model to use."""
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(
        in_features, num_classes=len(sub.CLASSES) + 1
    )
    return model
