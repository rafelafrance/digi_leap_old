#!/usr/bin/env python
"""Use a trained model to cut out labels on herbarium sheets."""

import argparse
import logging
import textwrap
from pathlib import Path

import torch
import torchvision
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import batched_nms
from tqdm import tqdm

import pylib.box_calc as calc
import pylib.const as config
import pylib.log as log
import pylib.subject as sub


def use(args):
    """Train the neural net."""
    torch.multiprocessing.set_sharing_strategy("file_system")

    state = torch.load(args.load_model)

    model = get_model()
    model.load_state_dict(state["model_state"])

    device = torch.device(args.device)
    model.to(device)

    model.eval()

    paths = list(args.sheets_dir.glob(args.glob))
    if args.limit:
        paths = paths[: args.limit]

    for path in tqdm(paths):
        try:
            with Image.open(path) as image:
                image = image.convert("L")
                data = transforms.ToTensor()(image)
        except UnidentifiedImageError:
            logging.warning(f"{path} is not an image")
            continue

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
                label_image = image.crop(box.tolist())
                class_name = sub.CLASS2NAME[label.item()]
                label_name = f"{path.stem}_{i}_{class_name}{path.suffix}"
                label_path = args.label_dir / label_name
                label_image.save(label_path, "JPEG")


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
    description = """Test a model that finds labels on herbarium sheets."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    defaults = config.get_config()

    arg_parser.add_argument(
        "--sheets-dir",
        default=defaults['sheets_dir'],
        type=Path,
        help="""Read training images corresponding to the JSONL file from this
            directory. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--glob",
        default=defaults['glob'],
        help="""Use images in the --image-dir with this glob pattern.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--load-model",
        default=defaults['load_model'],
        type=Path,
        help="""Use this model to find labels. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--label-dir",
        default=defaults['label_dir'],
        type=Path,
        help="Write cropped labels to this directory. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--device",
        default=defaults['device'],
        help="""Which GPU or CPU to use. Options are 'cpu', 'cuda:0', 'cuda:1' etc.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--nms-threshold",
        type=float,
        default=defaults['nms_threshold'],
        help="""The IoU threshold to use for non-maximum suppression (0.0 - 1.0].
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--sbs-threshold",
        type=float,
        default=defaults['sbs_threshold'],
        help="""The area threshold to use for small box suppression (0.0 - 1.0].
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    use(ARGS)

    log.finished()
