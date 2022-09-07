import csv
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import numpy as np

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
            "labels", cxn, label_set=label_set, label_conf=label_conf
        )
        for row in labels:
            name = Path(row["path"]).name
            if name in points:
                if name not in self.sheets:
                    self.sheets[name] = Sheet(row)
                self.sheets[name].labels.append(
                    Label(
                        class_=row["class"],
                        label_left=row["label_left"],
                        label_top=row["label_top"],
                        label_right=row["label_right"],
                        label_bottom=row["label_bottom"],
                    )
                )

    def build_new_labels(self, points):
        for path, point in points.items():
            if not point.missing or len(point.missing) < 2:
                continue
            if path in self.sheets:
                sheet = self.sheets[path]
                sheet.build_new_labels(point)

    def reclassify_old_labels(self, points):
        for path, point in points.items():
            if path in self.sheets:
                sheet = self.sheets[path]
                sheet.annotate(point)

        for sheet in self.sheets.values():
            for label in sheet.labels:
                label.reclassify()

    def insert(self, cxn):
        for sheet in self.sheets.values():
            sheet.insert(cxn)


class Sheet:
    sql = """
        insert into sheets
               ( sheet_set,  path,  width,  height,  coreid,  split)
        values (:sheet_set, :path, :width, :height, :coreid, :split)
        returning sheet_id
        """

    def __init__(self, label_rec):
        self.path: str = label_rec["path"]
        self.width: int = label_rec["width"]
        self.height: int = label_rec["height"]
        self.coreid: str = label_rec["coreid"]
        self.labels: list[Label] = []
        self.new_labels: list[Label] = []

    def build_new_labels(self, point):
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
        for label in self.labels:
            if (
                label.label_left <= annotation["x"] <= label.label_right
                and label.label_top <= annotation["y"] <= label.label_bottom
            ):
                return label
        return None

    def insert(self, cxn, sheet_set):
        sheet_id = cxn.execute(
            self.sql,
            {
                "sheet_set": sheet_set,
                "path": self.path,
                "width": self.width,
                "height": self.height,
                "coreid": self.coreid,
                "split": "",
            },
        )
        print(sheet_id)


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


def reconcile(args):
    with db.connect(args.database) as cxn:
        # run_id = db.insert_run(cxn, args)

        classifications = Classifications(args.unreconciled_csv)
        points = Points(classifications, args.increase_by)
        sheets = Sheets(cxn, points, args.label_conf, args.label_set)
        sheets.reclassify_old_labels(points)
        sheets.build_new_labels(points)
        sheets.insert(cxn)

        from pprint import pp

        for sheet in sheets.sheets.values():
            pp(sheet.__dict__)
            break
        # Write labels with click annotations to the database
        # Write new labels to database

        # db.update_run_finished(cxn, run_id)
