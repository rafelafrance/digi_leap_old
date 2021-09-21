"""Use a trained model to cut out labels on herbarium sheets."""

import logging
import os

import torch
import torchvision
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import batched_nms
from tqdm import tqdm

import digi_leap.pylib.box_calc as calc
import digi_leap.pylib.subject as sub


def use(args):
    """Train the neural net."""
    os.makedirs(args.label_dir, exist_ok=True)

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
