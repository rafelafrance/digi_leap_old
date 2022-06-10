import csv
import os
import warnings
from argparse import Namespace
from pathlib import Path

import torch
from PIL import Image
from PIL import ImageDraw
from tqdm import tqdm

from ... import box_calc
from ...db import db


def build(args: Namespace) -> None:
    os.makedirs(args.expedition_dir, exist_ok=True)

    select_sheets = """
        select * from sheets
        where sheet_id in (
            select distinct sheet_id from labels
            where label_set = ?
        )
        order by random()
        limit ?
        """
    select_labels = """
        select * from labels
        where sheet_id = ?
        and label_set = ?
        and label_conf >= ?
        """

    csv_path = args.expedition_dir / "manifest.csv"
    with db.connect(args.database) as cxn, open(csv_path, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            "sheet_id image reduced_by label_set label_conf database".split()
        )

        run_id = db.insert_run(cxn, args)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings

            sheet_args = [args.label_set, args.limit]
            for sheet in tqdm(db.execute(cxn, select_sheets, sheet_args)):
                image = Image.open(sheet["path"]).convert("RGB")
                draw = ImageDraw.Draw(image)

                labels = db.execute(
                    cxn,
                    select_labels,
                    [sheet["sheet_id"], args.label_set, args.label_conf],
                )
                labels = list(labels)
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
                boxes = box_calc.small_box_suppression(boxes, threshold=0.4)
                labels = [lb for i, lb in enumerate(labels) if i in boxes]

                for lb in labels:
                    color = "#d95f02" if lb["class"] == "Typewritten" else "#7570b3"
                    box = [
                        lb["label_left"],
                        lb["label_top"],
                        lb["label_right"],
                        lb["label_bottom"],
                    ]
                    draw.rectangle(box, outline=color, width=12)

                if args.reduce_by > 1:
                    image = image.reduce(args.reduce_by)

                name = Path(sheet["path"]).name
                path = args.expedition_dir / name
                image.save(str(path))

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
