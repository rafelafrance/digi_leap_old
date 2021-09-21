"""Reconcile data from a Label Babel expedition."""

import csv
import json
import logging
from collections import defaultdict

import numpy as np
import torch
from PIL import Image, UnidentifiedImageError
from torchvision.ops import clip_boxes_to_image
from tqdm import tqdm

from digi_leap.pylib import subject as sub


def reconcile(args):
    """Reconcile data from a Label Babel expedition."""
    classifications = get_classifications(args.unreconciled_csv)
    subjects = group_by_subject(classifications)
    subjects = subject_images(args.image_dir, subjects)
    subjects = merge_boxes(subjects)
    write_reconciled(subjects, args.reconciled_jsonl)


def get_classifications(unreconciled_csv):
    """Read unreconciled classifications."""
    with open(unreconciled_csv) as csv_file:
        reader = csv.DictReader(csv_file)
        classifications = [r for r in reader]
    return classifications


def group_by_subject(classifications):
    """Group classifications by subject."""
    subjects: dict[str, sub.Subject] = defaultdict(lambda: sub.Subject())

    for class_ in tqdm(classifications):
        sub_id = class_["subject_id"]

        subjects[sub_id].subject_id = sub_id
        subjects[sub_id].image_file = class_["subject_Filename"]

        coords = [v for k, v in class_.items() if k.startswith("Box(es): box") and v]
        boxes = np.array([sub.Subject.bbox_from_json(c) for c in coords if c])
        if len(boxes):
            subjects[sub_id].boxes = np.vstack((subjects[sub_id].boxes, boxes))

        selects = [
            (v if v else "")
            for k, v in class_.items()
            if k.startswith("Box(es): select")
        ]
        types = np.array(selects[: len(boxes)], dtype=str)
        if len(types):
            subjects[sub_id].types = np.hstack((subjects[sub_id].types, types))

    return list(subjects.values())


def subject_images(image_dir, subjects):
    """Clip boxes to the image size and remove bad images."""
    new_subjects = []
    for subject in tqdm(subjects):
        path = image_dir / subject.image_file
        try:
            image = Image.open(path)
            width, height = image.size
        except UnidentifiedImageError:
            logging.warning(f"{path} is not an image")
            continue

        boxes = torch.from_numpy(subject.boxes)
        boxes = clip_boxes_to_image(boxes, (height, width))
        subject.boxes = boxes.numpy()
        subject.image_size = (height, width)

        new_subjects.append(subject)

    return new_subjects


def merge_boxes(subjects):
    """Merge all boxes in each group of boxes into a single bounding box.

    There is a slight wrinkle here in that when labels are next to each other
    on the herbarium sheet some people lumped them into one large bounding
    box and others drew boxes around the individual labels. We'd prefer to
    have the individual bounding boxes for each label so we're going to do
    some extra processing to see if we can get them.
    """
    for subject in tqdm(subjects):
        subject.merge_box_groups()
    return subjects


def write_reconciled(subjects, reconciled_jsonl):
    """Write reconciled data to a CSV file."""
    with open(reconciled_jsonl, "w") as jsonl_file:
        for subject in tqdm(subjects):
            jsonl_file.write(json.dumps(subject.to_dict()) + "\n")
