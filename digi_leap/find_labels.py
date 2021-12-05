#!/usr/bin/env python3
"""Use a trained model to cut out labels on herbarium sheets."""
import argparse
import textwrap
from datetime import datetime
from pathlib import Path

import torch
import torchvision
from PIL import Image
from torchvision import transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import batched_nms
from tqdm import tqdm

from .pylib import box_calc as calc
from .pylib import db
from .pylib import subject as sub


def find(args):
    """Train the neural net."""
    torch.multiprocessing.set_sharing_strategy("file_system")

    state = torch.load(args.load_model)

    model = get_model()
    model.load_state_dict(state["model_state"])

    device = torch.device(args.device)
    model.to(device)

    model.eval()

    db.create_label_table(args.database, drop=True)
    sheets = db.select_sheets(args.database, limit=args.limit)

    label_batch = []

    run = datetime.now().isoformat(sep="_", timespec="seconds")

    for sheet in tqdm(sheets):

        with Image.open(sheet["path"]) as image:
            image = image.convert("L")
            data = transforms.ToTensor()(image)

        with torch.no_grad():
            preds = model([data.to(device)])

        for pred in preds:
            boxes = pred["boxes"].detach().cpu()
            labels = pred["labels"].detach().cpu()
            scores = pred["scores"].detach().cpu()

            idx = batched_nms(boxes, scores, labels, args.nms_threshold)
            boxes = boxes[idx, :]
            labels = labels[idx]

            idx = calc.small_box_suppression(boxes, args.sbs_threshold)
            boxes = boxes[idx, :]
            labels = labels[idx]

            for i, (box, label) in enumerate(zip(boxes, labels)):
                box = box.tolist()
                label_batch.append(
                    {
                        "sheet_id": sheet["sheet_id"],
                        "label_run": run,
                        "offset": i,
                        "class": sub.CLASS2NAME[label.item()],
                        "label_left": round(box[0]),
                        "label_top": round(box[1]),
                        "label_right": round(box[2]),
                        "label_bottom": round(box[3]),
                    }
                )

    db.insert_labels(args.database, label_batch)


def get_model():
    """Get the model to use."""
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(
        in_features, num_classes=len(sub.CLASSES) + 1
    )
    return model


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """Use a model that finds labels on herbarium sheets (inference)."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Path to the digi-leap database.""",
    )

    default = datetime.now().isoformat(sep="_", timespec="seconds")
    arg_parser.add_argument(
        "--find_run",
        "--find-run",
        default=default,
        help="""Name the label finder run. (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--load_model",
        "--load-model",
        type=Path,
        help="""Path, to the current model for finding labels on a herbarium sheet.""",
    )

    arg_parser.add_argument(
        "--device",
        default="cuda",
        help="""Which GPU or CPU to use. (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--nms_threshold",
        "--nms-threshold",
        type=float,
        default=0.3,
        help="""IoU overlap to use for non-maximum suppression.
            (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--sbs_threshold",
        "--sbs-threshold",
        type=float,
        default=0.95,
        help="""IoU overlap to use for small box suppression.
            (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    find(ARGS)
