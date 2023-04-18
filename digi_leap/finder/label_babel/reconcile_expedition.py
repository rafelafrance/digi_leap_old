import csv
from argparse import Namespace
from collections import defaultdict

import numpy as np
import pandas as pd
from tqdm import tqdm

from digi_leap.db import db
from digi_leap.pylib.subject import Subject


def reconcile(args: Namespace) -> None:
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        with open(args.unreconciled_csv) as csv_file:
            reader = csv.DictReader(csv_file)
            classifications = list(reader)

        subjects = get_subjects(classifications)

        for subject in tqdm(subjects):
            subject.merge_box_groups()

        df = get_reconciled_boxes(subjects, args.reconciled_set)
        df.to_sql("label_train", cxn, if_exists="append", index=False)

        db.update_run_finished(cxn, run_id)


def get_reconciled_boxes(subjects, reconciled_set):
    rec_boxes = []

    for subject in subjects:
        boxes = subject.merged_boxes

        if not boxes:
            continue

        classes = subject.merged_types

        if len(boxes) != len(classes):
            raise ValueError(f"Malformed subject {subject.subject_id}")

        for box, cls in zip(boxes, classes):
            rec_boxes.append(
                {
                    "sheet_id": subject.sheet_id,
                    "train_set": reconciled_set,
                    "train_class": cls,
                    "train_left": box[0],
                    "train_top": box[1],
                    "train_right": box[2],
                    "train_bottom": box[3],
                }
            )

    df = pd.DataFrame(rec_boxes)
    return df


def get_subjects(classifications):
    subs: dict[str, Subject] = defaultdict(Subject)

    for class_if in tqdm(classifications):
        sub_id = class_if["subject_id"]

        subs[sub_id].subject_id = sub_id
        subs[sub_id].sheet_id = class_if["sheet_id"]

        coords = [v for k, v in class_if.items() if k.startswith("Box(es): box") and v]
        boxes = np.array([Subject.bbox_from_json(c) for c in coords if c])
        if len(boxes):
            subs[sub_id].boxes = np.vstack((subs[sub_id].boxes, boxes))

        selects = [
            (v if v else "")
            for k, v in class_if.items()
            if k.startswith("Box(es): select")
        ]
        types = np.array(selects[: len(boxes)], dtype=str)
        if len(types):
            subs[sub_id].types = np.hstack((subs[sub_id].types, types))

    return list(subs.values())
