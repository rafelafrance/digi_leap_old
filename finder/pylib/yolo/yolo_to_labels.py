import csv
import json
import os
from collections import namedtuple
from pathlib import Path

from tqdm import tqdm

from .. import const, sheet

Scale = namedtuple("Scale", "path scale_x scale_y")


def to_labels(args):
    os.makedirs(args.label_dir, exist_ok=True)

    scales = get_sheet_scales(args.sheet_csv, args.yolo_size)

    with open(args.yolo_json) as in_file:
        labels = json.load(in_file)

    for label in tqdm(labels, desc="labels"):
        scale = scales[label["image_id"]]
        save_label(label, scale, args.label_dir)


def get_sheet_scales(sheet_csv, yolo_size):
    sheets = {}

    with open(sheet_csv) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in tqdm(reader, desc="scales"):
            path = Path(row["path"])
            image = sheet.sheet_image(path)
            width, height = image.size
            scale_x = width / yolo_size
            scale_y = height / yolo_size
            sheets[path.stem] = Scale(path, scale_x, scale_y)
    return sheets


def save_label(label, scale, label_dir):
    left, top = label["bbox"][0], label["bbox"][1]
    width, height = label["bbox"][2], label["bbox"][3]

    iid = label["image_id"]
    cls = const.CLASS2NAME[label["category_id"]]
    left = int(left * scale.scale_x)
    top = int(top * scale.scale_y)
    right = int((left + width) * scale.scale_x)
    bottom = int((top + height) * scale.scale_y)

    name = "_".join([iid, cls, left, top, right, bottom]) + scale.path.suffix

    image = sheet.sheet_image(label.path)
    image = image.crop((left, top, right, bottom))
    image.save(label_dir / name)
