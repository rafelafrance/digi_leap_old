#!/usr/bin/env python
"""Reconcile data from a Label Babel expedition."""

import csv
import logging
import textwrap
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image, UnidentifiedImageError
from sklearn.model_selection import train_test_split
from torchvision.ops import clip_boxes_to_image
from tqdm import tqdm

from digi_leap.log import finished, started
from digi_leap.subject import Subject


def reconcile(args):
    """Reconcile data from a Label Babel expedition."""
    classifications = get_classifications(args)
    subjects = group_by_subject(classifications)
    subjects = subject_images(args, subjects)
    subjects = merge_boxes(subjects)

    as_list = [s.as_dict() for s in subjects]
    df = pd.DataFrame(as_list)

    logging.info(f"Writing CSV files: {args.reconciled}")
    df.to_csv(args.reconciled, index=False)

    if args.split:
        train, test = train_test_split(df, test_size=args.split, random_state=args.seed)
        parent = args.reconciled.parent

        name = parent / f"{args.reconciled.stem}.train.{args.reconciled.suffix}"
        train.to_csv(name, index=False)

        name = parent / f"{args.reconciled.stem}.test.{args.reconciled.suffix}"
        test.to_csv(name, index=False)


def get_classifications(args):
    """Read unreconciled classifications."""
    with open(args.unreconciled) as csv_file:
        reader = csv.DictReader(csv_file)
        classifications = [r for r in reader]
    return classifications


def group_by_subject(classifications):
    """Group classifications by subject."""
    subjects: dict[str, Subject] = defaultdict(lambda: Subject())

    for class_ in tqdm(classifications):
        sub_id = class_["subject_id"]

        subjects[sub_id].subject_id = sub_id
        subjects[sub_id].image_file = class_["subject_Filename"]

        coords = [v for k, v in class_.items() if k.startswith("Box(es): box") and v]
        boxes = np.array([Subject.bbox_from_json(c) for c in coords if c])
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


def subject_images(args, subjects):
    """Clip boxes to the image size and remove bad images."""
    new_subjects = []
    for subject in tqdm(subjects):
        path = args.image_dir / subject.image_file
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


def to_dataframe(subjects):
    """Create the data frame for output."""
    as_list = [asdict(s) for s in subjects]
    df = pd.DataFrame(as_list)
    return df


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
    Reconcile data from a Label Babel expedition.

    This script merges bounding boxes and label types from unreconciled Label Babel
    classifications. We have to figure out which bounding boxes refer to which labels
    on the herbarium sheet and then merge them to find a single "best" bounding box.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--unreconciled",
        required=True,
        type=Path,
        help="""The unreconciled input CSV.""",
    )

    arg_parser.add_argument(
        "--image-dir",
        required=True,
        type=Path,
        help="""Read training images from this directory.""",
    )

    arg_parser.add_argument(
        "--reconciled",
        required=True,
        type=Path,
        help="""The reconciled output as a CSV file.""",
    )

    arg_parser.add_argument(
        "--split",
        type=float,
        default=0.2,
        help="""Fraction of subjects in the test dataset. (default: %(default)s)""",
    )

    arg_parser.add_argument("--seed", type=int, help="""Create a random seed.""")

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    reconcile(ARGS)

    finished()
