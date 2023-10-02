import warnings
from itertools import groupby

import numpy as np
from PIL import Image
from tqdm import tqdm

from ... import const
from ...db import db


def build(args):
    args.yolo_dir.mkdir(parents=True, exist_ok=True)

    with db.connect(args.database) as cxn:
        for split in ["train", "val", "test"]:
            image_dir, label_dir = make_dirs(args.yolo_dir, split)

            label_train = db.canned_select(
                cxn, "label_train", split=split, train_set=args.train_set
            )

            grouped = groupby(label_train, key=lambda lb: (lb["sheet_id"], lb["path"]))

            for (sheet_id, sheet_path), labels in tqdm(grouped):
                image_path = image_dir / f"{sheet_id}.jpg"
                text_path = label_dir / f"{sheet_id}.txt"
                write_sheet(sheet_path, image_path, args.image_size)
                write_labels(text_path, labels, args.image_size)


def write_sheet(sheet_path, image_path, image_size):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings

        image = Image.open(sheet_path).convert("RGB")
        image = image.resize((image_size, image_size))
        image.save(image_path)


def write_labels(text_path, labels, image_size):
    labels = list(labels)
    width, height = labels[0]["width"], labels[0]["height"]
    classes = [lb["train_class"] for lb in labels]
    boxes = np.array(
        [
            [lb["train_left"], lb["train_top"], lb["train_right"], lb["train_bottom"]]
            for lb in labels
        ],
        dtype=np.float64,
    )
    boxes = to_yolo_format(boxes, width, height, image_size)
    with open(text_path, "w") as txt_file:
        for label_class, box in zip(classes, boxes):
            label_class = const.CLASS2INT[label_class]
            bbox = np.array2string(box, formatter={"float_kind": lambda x: "%.6f" % x})
            line = f"{label_class} {bbox[1:-1]}\n"
            txt_file.write(line)


def to_yolo_format(bboxes, sheet_width, sheet_height, image_size):
    """Convert bounding boxes to YOLO format.

    resize to the new YOLO image size
    center x, center y, width, height
    convert to fraction of the YOLO image size
    """
    bboxes[:, [0, 2]] *= image_size / sheet_width  # Rescaled to new yolo image size
    bboxes[:, [1, 3]] *= image_size / sheet_height  # Resized to new yolo image size

    boxes = np.empty_like(bboxes)

    boxes[:, 0] = (bboxes[:, 2] + bboxes[:, 0]) / 2.0  # Center x
    boxes[:, 1] = (bboxes[:, 3] + bboxes[:, 1]) / 2.0  # Center y
    boxes[:, 2] = bboxes[:, 2] - bboxes[:, 0] + 1  # Box width
    boxes[:, 3] = bboxes[:, 3] - bboxes[:, 1] + 1  # Box height

    boxes[:, [0, 2]] /= image_size  # As a fraction of sheet width
    boxes[:, [1, 3]] /= image_size  # As a fraction of sheet height

    return boxes


def make_dirs(yolo_dir, split):
    image_dir = yolo_dir / split / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir = yolo_dir / split / "labels"
    label_dir.mkdir(parents=True, exist_ok=True)
    return image_dir, label_dir
