#!/usr/bin/env python
"""Train a model to recognize labels on herbarium sheets."""

import argparse
import logging
import textwrap
from pathlib import Path

import torch
import torchvision
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import batched_nms

import pylib.box_calc as calc
import pylib.const as const
import pylib.faster_rcnn_data as data
import pylib.log as log
import pylib.mean_avg_precision as mAP
import pylib.subject as sub
import pylib.util as util


def train(args):
    """Train the neural net."""
    torch.multiprocessing.set_sharing_strategy("file_system")

    state = torch.load(args.load_model) if args.load_model else {}

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

    train_loader, score_loader = get_loaders(args)

    start_epoch = state["epoch"] + 1 if state.get("epoch") else 1
    end_epoch = start_epoch + args.epochs + 1

    best_score = state["best_score"] if state.get("best_score") else -1.0
    best_loss = state["best_loss"] if state.get("best_loss") else 99999.0

    for epoch in range(start_epoch, end_epoch):
        train_loss = train_epoch(model, train_loader, device, optimizer)

        score = score_epoch(
            model, score_loader, device, args.nms_threshold, args.sbs_threshold
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
            args.save_model,
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


def get_loaders(args):
    """Get the data loaders."""
    subjects = data.FasterRcnnData.read_jsonl(args.reconciled_jsonl)

    if args.limit:
        subjects = subjects[: args.limit]

    train_subjects, score_subjects = train_test_split(subjects, test_size=args.split)
    train_dataset = data.FasterRcnnData(train_subjects, args.image_dir, augment=True)
    score_dataset = data.FasterRcnnData(score_subjects, args.image_dir)

    train_loader = DataLoader(
        train_dataset,
        shuffle=True,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=util.collate_fn,
    )

    score_loader = DataLoader(
        score_dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=util.collate_fn,
    )

    return train_loader, score_loader


def get_model():
    """Get the model to use."""
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(
        in_features, num_classes=len(sub.CLASSES) + 1
    )
    return model


def parse_args():
    """Process command-line arguments."""
    description = """Train a model to find labels on herbarium sheets."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--reconciled-jsonl",
        required=True,
        type=Path,
        help="""The JSONL file containing reconciled bounding boxes.""",
    )

    arg_parser.add_argument(
        "--image-dir",
        required=True,
        type=Path,
        help="""Read training images corresponding to the JSONL file from this
            directory.""",
    )

    arg_parser.add_argument(
        "--save-model",
        type=Path,
        required=True,
        help="""Save model state to this file.""",
    )

    arg_parser.add_argument(
        "--load-model",
        type=Path,
        help="""Load this model state to continue training.""",
    )

    arg_parser.add_argument(
        "--split",
        type=float,
        default=0.25,
        help="""Fraction of subjects in the score dataset. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--device",
        default=const.DEVICE,
        help="""Which GPU or CPU to use. Options are 'cpu', 'cuda:0', 'cuda:1' etc.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="""How many epochs to train. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.005,
        help="""Initial learning rate. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--batch-size",
        type=int,
        default=const.GPU_BATCH,
        help="""Input batch size. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--workers",
        type=int,
        default=const.WORKERS,
        help="""Number of workers for loading data. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    arg_parser.add_argument(
        "--nms-threshold",
        type=float,
        default=const.NMS_THRESHOLD,
        help="""The IoU threshold to use for non-maximum suppression (0.0 - 1.0].
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--sbs-threshold",
        type=float,
        default=const.SBS_THRESHOLD,
        help="""The area threshold to use for small box suppression (0.0 - 1.0].
            (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    train(ARGS)

    log.finished()