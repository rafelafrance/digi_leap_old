import csv
import os
import warnings
from argparse import Namespace
from pathlib import Path

import torch
from PIL import Image
from PIL import ImageDraw
from tqdm import tqdm

from digi_leap.db import db
from digi_leap.pylib import box_calc


def build(args: Namespace) -> None:
    os.makedirs(args.expedition_dir, exist_ok=True)

    sheet_sql = """
        select * from sheets
        where sheet_id in (
            select distinct sheet_id from labels
            where label_set = :label_set
        )
        order by random()
        limit :limit
        """

    csv_path = args.expedition_dir / "manifest.csv"
    with db.connect(args.database) as cxn, open(csv_path, "w") as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(
            "sheet_id image reduced_by label_set label_conf database".split()
        )

        run_id = db.insert_run(cxn, args)

        sheets = db.select(cxn, sheet_sql, label_set=args.label_set, limit=args.limit)
        for sheet in tqdm(sheets):
            labels = select_labels(cxn, sheet, args.label_set, args.label_conf)
            labels = filter_labels(labels)

            image = create_sheet_image(sheet["path"], labels, args.reduce_by)
            name = save_image(image, sheet, args.expedition_dir)

            writer.writerow(
                [
                    sheet["sheet_id"],
                    name,
                    args.reduce_by,
                    args.label_set,
                    args.label_conf,
                    args.database,
                ]
            )

        db.update_run_finished(cxn, run_id)


def select_labels(cxn, sheet, label_set, label_conf):
    label_sql = """
        select * from labels
        where sheet_id = :sheet_id
        and label_set = :label_set
        and label_conf >= :label_conf
        """
    labels = db.select(
        cxn,
        label_sql,
        sheet_id=sheet["sheet_id"],
        label_set=label_set,
        label_conf=label_conf,
    )
    return list(labels)


def filter_labels(labels, threshold=0.4):
    boxes = [
        [
            lb["label_left"],
            lb["label_top"],
            lb["label_right"],
            lb["label_bottom"],
        ]
        for lb in labels
    ]
    boxes = torch.tensor(boxes)
    boxes = box_calc.small_box_suppression(boxes, threshold=threshold)
    labels = [lb for i, lb in enumerate(labels) if i in boxes]
    return labels


def create_sheet_image(path, labels, reduce_by=1):
    path = path.removeprefix("../")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings

        image = Image.open(path).convert("RGB")
        draw = ImageDraw.Draw(image)

        for lb in labels:
            color = "#d95f02" if lb["class"] == "Typewritten" else "#7570b3"
            box = (
                lb["label_left"],
                lb["label_top"],
                lb["label_right"],
                lb["label_bottom"],
            )
            draw.rectangle(box, outline=color, width=12)

        if reduce_by > 1:
            image = image.reduce(reduce_by)

    return image


def save_image(image, sheet, expedition_dir):
    name = Path(sheet["path"]).name
    path = expedition_dir / name
    image.save(str(path))
    return name
