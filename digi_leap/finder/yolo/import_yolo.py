"""Read a JSON file of YOLO results into the database."""
import json

from digi_leap.db import db
from digi_leap.pylib import const


def load(args):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        rows = db.canned_select(
            cxn, "label_train_split", train_set=args.train_set, split="test"
        )
        sheets: dict[str, tuple] = {}

        for row in rows:
            scale_x = row["width"] / args.image_size
            scale_y = row["height"] / args.image_size
            sheets[row["sheet_id"]] = scale_x, scale_y

        with open(args.yolo_json) as in_file:
            rows = json.load(in_file)

        batch = []
        for row in rows:
            scale_x, scale_y = sheets[row["image_id"]]

            left, top = row["bbox"][0], row["bbox"][1]
            width, height = (
                row["bbox"][2],
                row["bbox"][3],
            )

            record = {
                "sheet_id": row["image_id"],
                "test_set": args.test_set,
                "train_set": args.train_set,
                "test_class": const.CLASS2NAME[row["category_id"]],
                "test_conf": row["score"],
                "test_left": int(left * scale_x),
                "test_right": int((left + width) * scale_x),
                "test_top": int(top * scale_y),
                "test_bottom": int((top + height) * scale_y),
            }
            batch.append(record)

        db.canned_delete(
            cxn, "label_tests", test_set=args.test_set, train_set=args.train_set
        )
        db.canned_insert(cxn, "label_tests", batch)

        db.update_run_finished(cxn, run_id)
