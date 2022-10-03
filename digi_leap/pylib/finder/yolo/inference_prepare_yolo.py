import os
import warnings
from argparse import Namespace

from PIL import Image
from tqdm import tqdm

from ...db import db


def build(args: Namespace) -> None:
    os.makedirs(args.yolo_dir, exist_ok=True)

    sheet_sql = """
        select * from sheets
        where  coreid not in (
            select coreid from sheets
            where  sheet_set in (
                select distinct sheet_set from sheets where sheet_set <> 'original'
            )
        )
        order by random()
        limit :limit
        """

    batch: list[dict] = []

    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        sheets = db.select(cxn, sheet_sql, limit=args.limit)
        for sheet in tqdm(sheets):
            batch.append(
                {
                    "sheet_set": args.sheet_set,
                    "path": sheet["path"],
                    "width": sheet["width"],
                    "height": sheet["height"],
                    "coreid": sheet["coreid"],
                    "split": "",
                }
            )
            yolo_image(sheet["path"], sheet["coreid"], args.yolo_dir, args.image_size)

        db.canned_delete(cxn, "sheets", sheet_set=args.sheet_set)
        db.canned_insert(cxn, "sheets", batch)

        db.update_run_finished(cxn, run_id)


def yolo_image(sheet_path, coreid, yolo_dir, image_size):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        image_path = yolo_dir / f"{coreid}.jpg"

        image = Image.open(sheet_path).convert("RGB")
        image = image.resize((image_size, image_size))
        image.save(image_path)
