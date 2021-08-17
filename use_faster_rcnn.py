#!/usr/bin/env python
"""Use a model cut out labels on herbarium sheets."""

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

from digi_leap.const import NMS_THRESHOLD
from digi_leap.log import finished, started
from digi_leap.subject import CLASS2NAME, CLASSES


def use(args):
    """Train the neural net."""
    torch.multiprocessing.set_sharing_strategy("file_system")

    state = torch.load(args.load_model)

    model = get_model()
    model.load_state_dict(state["model_state"])

    device = torch.device(args.device)
    model.to(device)

    model.eval()

    for path in tqdm(args.image_dir.glob(args.glob)):
        try:
            with Image.open(path) as image:
                image = image.convert("L")
                image = transforms.ToTensor()(image)
        except UnidentifiedImageError:
            logging.warning(f"{path} is not an image")
            continue

        preds = model([image.to(device)])

        image = image.detach().cpu()
        image = transforms.ToPILImage()(image)

        for pred in preds:
            idx = batched_nms(
                pred["boxes"], pred["scores"], pred["labels"], args.nms_threshold
            )
            boxes = pred["boxes"][idx, :].detach().cpu()
            labels = pred["labels"][idx].detach().cpu()
            for i, (box, label) in enumerate(zip(boxes, labels)):
                label_image = image.crop(box.tolist())
                label_name = f"{path.stem}_{i}_{CLASS2NAME[label.item()]}{path.suffix}"
                label_path = args.label_dir / label_name
                label_image.save(label_path, "JPEG")


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
        "--image-dir",
        required=True,
        type=Path,
        help="""Read training images corresponding to the JSONL file from this
            directory.""",
    )

    arg_parser.add_argument(
        "--glob",
        default="*.jpg",
        help="""Use images in the --image-dir with this glob pattern.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--load-model",
        required=True,
        type=Path,
        help="""Load this model state to continue training.""",
    )

    arg_parser.add_argument(
        "--label-dir",
        required=True,
        type=Path,
        help="Write cropped labels to this directory.",
    )

    default = "cuda:0" if torch.cuda.is_available() else "cpu"
    arg_parser.add_argument(
        "--device",
        default=default,
        help="""Which GPU or CPU to use. Options are 'cpu', 'cuda:0', 'cuda:1' etc.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--nms-threshold",
        type=float,
        default=NMS_THRESHOLD,
        help="""The IoU threshold to use for non-maximum suppression (0.0 - 1.0].
            (default: %(default)s)""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    use(ARGS)

    finished()
