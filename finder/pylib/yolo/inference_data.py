import csv
import os
from argparse import Namespace
from pathlib import Path

from tqdm import tqdm

from .. import sheet_util


def build(args: Namespace) -> None:
    os.makedirs(args.yolo_images, exist_ok=True)

    with open(args.sheet_csv) as csv_file:
        reader = csv.DictReader(csv_file)
        sheets = [r["path"] for r in reader]

    for path in tqdm(sheets):
        path = Path(path)
        sheet_util.to_yolo_image(path, args.yolo_images, args.yolo_size)
