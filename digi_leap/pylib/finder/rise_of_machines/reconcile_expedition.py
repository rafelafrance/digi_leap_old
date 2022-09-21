import csv
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import numpy as np
import torch

from ... import box_calc as calc
from ...db import db


class Classifications(defaultdict):
    def __init__(self, unreconciled_csv):
        super().__init__(list)
        with open(unreconciled_csv) as csv_file:
            reader = csv.DictReader(csv_file)
            rows = [r for r in reader]
        for row in rows:
            self[row["Filename"]].append(dict(row))


class Points(defaultdict):
    def __init__(self, classifications, increase_by=1):
        super().__init__(Point)
        for path, rows in classifications.items():
            for row in rows:
                self[path].missing += self.new_points(row, " missing:", increase_by)
                self[path].correct += self.new_points(row, " Correct:", increase_by)
                self[path].incorrect += self.new_points(row, " Incorrect:", increase_by)

    @staticmethod
    def new_points(row, label, increase_by):
        points = defaultdict(dict)
        for key, value in row.items():
            if key.find(label) > -1 and value != "":
                point, coord = key.split(":")
                points[point][coord.strip()] = round(float(value) * increase_by)
        return list(points.values())


@dataclass()
class Point:
    correct: list[dict] = field(default_factory=list)
    incorrect: list[dict] = field(default_factory=list)
    missing: list[dict] = field(default_factory=list)


class Sheets:
    def __init__(self, cxn, points, label_conf, label_set):
        self.sheets: dict[str, Sheet] = {}
        labels = db.canned_select(
            cxn, "labels", label_set=label_set, label_conf=label_conf
        )
        for label_rec in labels:
            name = Path(label_rec["path"]).name
            if name in points:
                if name not in self.sheets:
                    self.sheets[name] = Sheet(label_rec)
                self.sheets[name].add_old_label(label_rec)
        for sheet in self.sheets.values():
            sheet.filter_labels()

    def build_new_labels(self, points):
        for path, point in points.items():
            if not point.missing or len(point.missing) < 2:
                continue
            if path in self.sheets:
                sheet = self.sheets[path]
                sheet.add_new_labels(point)

    def reclassify_old_labels(self, points):
        for path, point in points.items():
            if path in self.sheets:
                sheet = self.sheets[path]
                sheet.annotate(point)

        for sheet in self.sheets.values():
            for label in sheet.old_labels:
                label.reclassify()

    def insert(self, cxn, sheet_set, train_set):
        db.canned_delete(cxn, "sheets", sheet_set=sheet_set)
        db.canned_delete(cxn, "label_train", train_set=train_set)
        for sheet in self.sheets.values():
            sheet.insert(cxn, sheet_set, train_set)


class Sheet:
    def __init__(self, label_rec):
        self.path: str = label_rec["path"]
        self.width: int = label_rec["width"]
        self.height: int = label_rec["height"]
        self.coreid: str = label_rec["coreid"]
        self.old_labels: list[Label] = []
        self.new_labels: list[Label] = []

    def add_old_label(self, label_rec):
        self.old_labels.append(
            Label(
                class_=label_rec["class"],
                label_left=label_rec["label_left"],
                label_top=label_rec["label_top"],
                label_right=label_rec["label_right"],
                label_bottom=label_rec["label_bottom"],
            )
        )

    def filter_labels(self, threshold=0.4):
        boxes = [
            [
                lb.label_left,
                lb.label_top,
                lb.label_right,
                lb.label_bottom,
            ]
            for lb in self.old_labels
        ]
        boxes = torch.tensor(boxes)
        boxes = calc.small_box_suppression(boxes, threshold=threshold)
        labels = [lb for i, lb in enumerate(self.old_labels) if i in boxes]
        self.old_labels = labels

    def add_new_labels(self, point):
        boxes = [[m["left"], m["top"], m["right"], m["bottom"]] for m in point.missing]
        boxes = np.array(boxes, dtype=np.int32)
        groups = calc.overlapping_boxes(boxes)
        max_group = np.max(groups)
        for group in range(1, max_group + 1):
            box_group = boxes[groups == group]
            if len(box_group) <= 1:
                continue
            box_min = np.min(box_group, axis=0)
            box_max = np.max(box_group, axis=0)

            label = Label(
                label_left=box_min[0],
                label_top=box_min[1],
                label_right=box_max[2],
                label_bottom=box_max[3],
            )
            self.new_labels.append(label)

    def annotate(self, point):
        for annotation in point.correct:
            if label := self.find_label(annotation):
                label.votes += 1

        for annotation in point.incorrect:
            if label := self.find_label(annotation):
                label.votes -= 1

    def find_label(self, annotation):
        for label in self.old_labels:
            if (
                label.label_left <= annotation["x"] <= label.label_right
                and label.label_top <= annotation["y"] <= label.label_bottom
            ):
                return label
        return None

    def insert(self, cxn, sheet_set, train_set):
        sql = """
            insert into sheets
                   ( sheet_set,  path,  width,  height,  coreid,  split)
            values (:sheet_set, :path, :width, :height, :coreid, :split)
            returning sheet_id
            """
        sheet_id = cxn.execute(
            sql,
            {
                "sheet_set": sheet_set,
                "path": self.path,
                "width": self.width,
                "height": self.height,
                "coreid": self.coreid,
                "split": "",
            },
        ).fetchone()[0]

        batch = []
        for label in self.old_labels + self.new_labels:
            batch.append(label.build_insert(sheet_id, self, train_set))
        db.canned_insert(cxn, "label_train", batch)


@dataclass()
class Label:
    class_: str = "Typewritten"
    label_left: str = 0
    label_top: str = 0
    label_right: str = 0
    label_bottom: str = 0
    votes: int = 0

    def reclassify(self):
        if self.votes > 0 and self.class_ != "Typewritten":
            self.class_ = "Other"
        elif self.votes <= 0 and self.class_ == "Typewritten":
            self.class_ = "Other"
        elif self.votes <= 0 and self.class_ != "Typewritten":
            self.class_ = "Typewritten"

    def build_insert(self, sheet_id, sheet, label_set):
        label = {
            "sheet_id": sheet_id,
            "train_set": label_set,
            "train_class": self.class_,
            "train_left": max(0, int(self.label_left)),
            "train_top": max(0, int(self.label_top)),
            "train_right": min(sheet.width - 1, int(self.label_right)),
            "train_bottom": min(sheet.height - 1, int(self.label_bottom)),
        }
        return label


def reconcile(args):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        classifications = Classifications(args.unreconciled_csv)
        points = Points(classifications, args.increase_by)
        sheets = Sheets(cxn, points, args.label_conf, args.label_set)
        sheets.reclassify_old_labels(points)
        sheets.build_new_labels(points)
        sheets.insert(cxn, args.sheet_set, args.train_set)

        db.update_run_finished(cxn, run_id)
