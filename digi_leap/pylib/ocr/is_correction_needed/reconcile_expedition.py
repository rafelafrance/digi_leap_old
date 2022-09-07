# import csv
# from collections import defaultdict
# from pathlib import Path
#
# from ...db import db


def reconcile(args):
    print(args)
    # with db.connect(args.database) as cxn:
    #     # run_id = db.insert_run(cxn, args)
    #
    #     classifications = read_classifications(args.unreconciled_csv)
    #     points = classifications_to_points(classifications, args.increase_by)
    #     sheets = select_sheet_labels(cxn, args.label_set)
    #     points_to_annotations(sheets, points)
    #
    #     # Write new label training data
    #
    #     # db.update_run_finished(cxn, run_id)


# def read_classifications(unreconciled_csv):
#     with open(unreconciled_csv) as csv_file:
#         reader = csv.DictReader(csv_file)
#         rows = [r for r in reader]
#
#     classifications = defaultdict(list)
#     for row in rows:
#         classifications[row["Filename"]].append(dict(row))
#
#     return classifications
#
#
# def select_sheet_labels(cxn, label_set):
#     sheets = defaultdict(list)
#     for row in db.canned_select("labels", cxn, label_set=label_set):
#         name = Path(row["path"]).name
#         sheets[name].append(dict(row))
#     return sheets
#
#
# def classifications_to_points(classifications, increase_by=1):
#     points = defaultdict(lambda: {"correct": [], "incorrect": [], "missing": []})
#     for path, rows in classifications.items():
#         for row in rows:
#             points[path]["missing"] += new_points(row, " missing:", increase_by)
#             points[path]["correct"] += new_points(row, " Correct:", increase_by)
#             points[path]["incorrect"] += new_points(row, " Incorrect:", increase_by)
#     return points
#
#
# def new_points(row, label, increase_by):
#     points = defaultdict(dict)
#     for key, value in row.items():
#         if key.find(label) > -1 and value != "":
#             point, coord = key.split(":")
#             points[point][coord.strip()] = float(value) * increase_by
#     return list(points.values())
#
#
# def points_to_annotations(sheets, points):
#     for labels in sheets.values():
#         for lb in labels:
#             lb["annotations"] = []
#
#     whiff = 0
#     for path, annotations in points.items():
#         sheet = sheets[path]
#         for point in annotations["correct"]:
#             if label := find_label(sheet, point):
#                 label["annotations"].append("correct")
#             else:
#                 whiff += 1
#         for point in annotations["incorrect"]:
#             if label := find_label(sheet, point):
#                 label["annotations"].append("incorrect")
#             else:
#                 whiff += 1
#     return whiff
#
#
# def find_label(sheet, point):
#     for label in sheet:
#         if (
#             label["label_left"] <= point["x"] <= label["label_right"]
#             and label["label_top"] <= point["y"] <= label["label_bottom"]
#         ):
#             return label
#     return None
