#!/usr/bin/env python
"""Test a model recognizes labels on herbarium sheets."""

import argparse
import logging
import textwrap
from copy import deepcopy
from pathlib import Path

import torch
import torchvision
from torch.utils.data import DataLoader
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import batched_nms

from digi_leap.faster_rcnn_data import FasterRcnnData
from digi_leap.log import finished, started
from digi_leap.mean_avg_precision import mAP_iou
from digi_leap.subject import CLASSES
from digi_leap.util import collate_fn


def test(args):
    """Train the neural net."""
    torch.multiprocessing.set_sharing_strategy("file_system")

    state = torch.load(args.load_model)

    model = get_model()
    model.load_state_dict(state["model_state"])

    device = torch.device(args.device)
    model.to(device)

    score_loader = get_loaders(args)

    train_score = state["best_score"] if state.get("best_score") else -1.0

    score = score_epoch(model, score_loader, device)
    log_results(score, train_score)


def score_epoch(model, loader, device, iou_threshold=0.3):
    """Evaluate the model."""
    model.eval()

    all_results = []

    for images, targets in loader:
        images = list(image.to(device) for image in images)

        with torch.no_grad:
            preds = model(images)

        for pred, target in zip(preds, targets):
            idx = batched_nms(
                pred["boxes"], pred["scores"], pred["labels"], iou_threshold
            )
            all_results.append(
                {
                    "image_id": deepcopy(target["image_id"]),
                    "true_boxes": deepcopy(target["boxes"]),
                    "true_labels": deepcopy(target["labels"]),
                    "pred_boxes": pred["boxes"][idx, :].detach().cpu(),
                    "pred_labels": pred["labels"][idx].detach().cpu(),
                    "pred_scores": pred["scores"][idx].detach().cpu(),
                }
            )

    score = mAP_iou(all_results)
    return score


def log_results(score, train_score):
    """Print results to screen."""
    logging.info(f"Train mAP: {train_score:0.3f}, test mAP: {score:0.3f}")


def get_loaders(args):
    """Get the data loaders."""
    subjects = FasterRcnnData.read_jsonl(args.reconciled_jsonl)

    if args.limit:
        subjects = subjects[: args.limit]

    score_dataset = FasterRcnnData(subjects, args.image_dir)

    score_loader = DataLoader(
        score_dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=collate_fn,
    )

    return score_loader


def get_model():
    """Get the model to use."""
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(
        in_features, num_classes=len(CLASSES) + 1
    )
    return model


def parse_args():
    """Process command-line arguments."""
    description = """Test a model that finds labels on herbarium sheets."""
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
        help="Read test images corresponding to the JSONL file from this directory.",
    )

    arg_parser.add_argument(
        "--load-model",
        required=True,
        type=Path,
        help="""Load this model state testing.""",
    )

    default = "cuda:0" if torch.cuda.is_available() else "cpu"
    arg_parser.add_argument(
        "--device",
        default=default,
        help="""Which GPU or CPU to use. Options are 'cpu', 'cuda:0', 'cuda:1' etc.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help="""Input batch size. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="""Number of workers for loading data. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    test(ARGS)

    finished()
