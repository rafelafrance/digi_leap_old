from argparse import Namespace

from digi_leap.db import db
from digi_leap.pylib import const


def ingest(args: Namespace) -> None:
    with db.connect(args.database) as cxn:

        sheets = db.canned_select(cxn, "sheets", sheet_set=args.sheet_set)
        sheets = {s["core_id"]: s for s in sheets}

        labels = read_yolo_labels(args.yolo_dir)
        filter_labels(labels)

        batch = resize_labels(labels, sheets, args.label_set)

        db.canned_delete(cxn, "labels", label_set=args.label_set)
        db.canned_insert(cxn, "labels", batch)


def filter_labels(results, threshold=3.0):
    for core_id, labels in results.items():
        labels = [lb for lb in labels if lb["wide"] < 0.5 and lb["high"] < 0.5]
        labels = [lb for lb in labels if (lb["high"] / lb["wide"]) < threshold]
        results[core_id] = labels


def resize_labels(results, sheets, label_set):
    batch = []

    for core_id, labels in results.items():
        sheet = sheets[core_id]

        for lb in labels:
            rad_x = lb["wide"] / 2.0
            rad_y = lb["high"] / 2.0

            batch.append(
                {
                    "sheet_id": sheet["sheet_id"],
                    "label_set": label_set,
                    "class": const.CLASS2NAME[lb["class"]],
                    "label_conf": lb["conf"],
                    "label_left": int((lb["center_x"] - rad_x) * sheet["width"]),
                    "label_top": int((lb["center_y"] - rad_y) * sheet["height"]),
                    "label_right": int((lb["center_x"] + rad_x) * sheet["width"]),
                    "label_bottom": int((lb["center_y"] + rad_y) * sheet["height"]),
                }
            )

    return batch


def read_yolo_labels(yolo_dir):
    results = {}
    paths = yolo_dir.glob("*.txt")
    for path in paths:
        core_id = path.stem
        results[core_id] = []
        with open(path) as in_file:
            lines = in_file.readlines()
            for ln in lines:
                cls, left, top, wide, high, conf = ln.split()
                results[core_id].append(
                    {
                        "class": int(cls),
                        "conf": float(conf),
                        "center_x": float(left),
                        "center_y": float(top),
                        "wide": float(wide),
                        "high": float(high),
                    }
                )
    return results
