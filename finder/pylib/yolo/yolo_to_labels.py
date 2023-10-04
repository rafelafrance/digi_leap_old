import csv
import os
from pathlib import Path

from tqdm import tqdm

from .. import const, sheet_util


def to_labels(args):
    os.makedirs(args.label_dir, exist_ok=True)

    sheet_paths = {}
    with open(args.sheet_csv) as f:
        for row in csv.DictReader(f):
            path = Path(row["path"])
            sheet_paths[path.stem] = path

    label_paths = sorted(args.yolo_labels.glob("*.txt"))
    for label_path in tqdm(label_paths):
        sheet_path = sheet_paths.get(label_path.stem)
        if not sheet_path:
            continue

        sheet_image = sheet_util.sheet_image(sheet_path)

        with open(label_path) as lb:
            lines = lb.readlines()

        stem = label_path.stem

        for ln in lines:
            cls, left, top, right, bottom = from_yolo_format(ln, sheet_image)

            name = "_".join([stem, cls, str(left), str(top), str(right), str(bottom)])
            name += sheet_path.suffix

            label_image = sheet_image.crop((left, top, right, bottom))
            label_image.save(args.label_dir / name)


def from_yolo_format(ln, sheet_image):
    """Convert YOLO coordinates to image coordinates."""
    cls, center_x, center_y, width, height, *_ = ln.split()

    cls = const.CLASS2NAME[int(cls)]

    # Scale from fraction to sheet image size
    sheet_width, sheet_height = sheet_image.size
    center_x = float(center_x) * sheet_width
    center_y = float(center_y) * sheet_height
    radius_x = float(width) * sheet_width / 2
    radius_y = float(height) * sheet_height / 2

    # Calculate label's pixel coordinates
    left = round(center_x - radius_x)
    top = round(center_y - radius_y)
    right = round(center_x + radius_x)
    bottom = round(center_y + radius_y)

    return cls, left, top, right, bottom
