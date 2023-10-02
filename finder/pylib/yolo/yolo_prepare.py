import csv
import logging
import os
import warnings
from argparse import Namespace
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm

from .. import const

EXCEPTIONS = (UnidentifiedImageError, ValueError, TypeError, FileNotFoundError)


def build(args: Namespace) -> None:
    os.makedirs(args.yolo_images, exist_ok=True)
    os.makedirs(args.yolo_labels, exist_ok=True)

    sheets = get_sheets(args.label_csv)

    for path, labels in tqdm(sheets.items()):
        sheet = Path(path)
        image_size = yolo_image(sheet, args.yolo_images, args.image_size)
        if image_size is not None:
            write_labels(args.yolo_labels, labels, image_size, args.yolo_size)


def get_sheets(label_csv) -> dict[list[dict]]:
    with open(label_csv) as csv_file:
        reader = csv.DictReader(csv_file)
        sheets = defaultdict(list)
        for label in reader:
            path = label["path"]
            if label["class"]:
                sheets[path].append(label)
            elif path not in sheets:
                sheets[path] = []
    return sheets


def yolo_image(sheet, yolo_images, yolo_size) -> tuple[int, int] | None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        yolo = yolo_images / sheet.name

        try:
            image = Image.open(sheet).convert("RGB")
            resized = image.resize((yolo_size, yolo_size))
            resized.save(yolo)
            return image.size

        except EXCEPTIONS as err:
            logging.error(f"Could not prepare {sheet.name}: {err}")
            return None


def write_labels(text_path, labels, image_size, yolo_size):
    classes = [lb["class"] for lb in labels]
    boxes = np.array(
        [[lb["left"], lb["top"], lb["right"], lb["bottom"]] for lb in labels],
        dtype=np.float64,
    )
    width, height = image_size
    boxes = to_yolo_format(boxes, width, height, yolo_size)
    with open(text_path, "w") as txt_file:
        for label_class, box in zip(classes, boxes):
            label_class = const.CLASS2INT[label_class]
            bbox = np.array2string(box, formatter={"float_kind": lambda x: "%.6f" % x})
            line = f"{label_class} {bbox[1:-1]}\n"
            txt_file.write(line)


def to_yolo_format(bboxes, sheet_width, sheet_height, yolo_size):
    """Convert bounding boxes to YOLO format.

    resize to the new YOLO image size
    center x, center y, width, height
    convert to fraction of the YOLO image size
    """
    bboxes[:, [0, 2]] *= yolo_size / sheet_width  # Rescaled to new yolo image size
    bboxes[:, [1, 3]] *= yolo_size / sheet_height  # Resized to new yolo image size

    boxes = np.empty_like(bboxes)

    boxes[:, 0] = (bboxes[:, 2] + bboxes[:, 0]) / 2.0  # Center x
    boxes[:, 1] = (bboxes[:, 3] + bboxes[:, 1]) / 2.0  # Center y
    boxes[:, 2] = bboxes[:, 2] - bboxes[:, 0] + 1  # Box width
    boxes[:, 3] = bboxes[:, 3] - bboxes[:, 1] + 1  # Box height

    boxes[:, [0, 2]] /= yolo_size  # As a fraction of sheet width
    boxes[:, [1, 3]] /= yolo_size  # As a fraction of sheet height

    return boxes
