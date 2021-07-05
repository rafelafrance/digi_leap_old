#!/usr/bin/env python
"""Reconcile data from a Label Babel expedition."""

import csv
import textwrap
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, UnidentifiedImageError
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from digi_leap.log import finished, started
from digi_leap.subject import Subject


def reconcile(args):
    """Reconcile data from a Label Babel expedition."""
    classifications = get_classifications(args)
    subjects = group_by_subject(classifications)
    subjects = merge_boxes(subjects)
    rows = get_image_sizes(args, subjects)
    write_csv(args, rows)


def get_classifications(args):
    """Read unreconciled classifications."""
    with open(args.unreconciled) as csv_file:
        reader = csv.DictReader(csv_file)
        classifications = [r for r in reader]
    return classifications


def group_by_subject(classifications):
    """Group classifications by subject."""
    subs: dict[str, Subject] = defaultdict(lambda: Subject())

    for classify in tqdm(classifications):
        sub_id = classify['subject_id']

        subs[sub_id].subject_id = sub_id
        subs[sub_id].image_file = classify['subject_Filename']

        coords = [v for k, v in classify.items() if k.startswith('Box(es): box') and v]
        boxes = np.array([Subject.bbox_from_json(c) for c in coords if c])
        if len(boxes):
            subs[sub_id].boxes = np.vstack((subs[sub_id].boxes, boxes))

        selects = [(v if v else '') for k, v in classify.items()
                   if k.startswith('Box(es): select')]
        types = np.array(selects[:len(boxes)], dtype=str)
        if len(types):
            subs[sub_id].types = np.hstack((subs[sub_id].types, types))

    return list(subs.values())


def merge_boxes(subjects):
    """Merge all boxes in each group of boxes into a single bounding box.

    There is a slight wrinkle here in that when labels are next to each other
    on the herbarium sheet some people lumped them into one large bounding
    box and others drew boxes around the individual labels. We'd prefer to
    have the individual bounding boxes for each label so we're going to do
    some extra processing to see if we can get them.
    """
    new_subjects = []

    for subject in tqdm(subjects):
        subject.merge_box_groups()
        new_subjects.append(subject.to_dict(everything=True))

    return new_subjects


def get_image_sizes(args, subjects):
    """Get image sizes."""
    new_rows = []

    for subject in subjects:
        path = args.image_file / subject['image_file']
        try:
            image = Image.open(path)
            width, height = image.size
        except UnidentifiedImageError:
            continue
        subject['image_size'] = {'width': width, 'height': height}
        new_rows.append(subject)

    return new_rows


def write_csv(args, rows):
    """Create the data frame for output."""
    df = pd.DataFrame(rows).fillna('')

    # Sort columns
    columns = """ subject_id  image_file image_size """.split()

    boxes = [k for k in df.columns if k.startswith('merged_box_')]
    types = [k for k in df.columns if k.startswith('merged_type_')]
    columns += [c for s in zip(boxes, types) for c in s]

    boxes = [k for k in df.columns if k.startswith('removed_box_')]
    types = [k for k in df.columns if k.startswith('removed_type_')]
    columns += [c for s in zip(boxes, types) for c in s]

    boxes = [k for k in df.columns if k.startswith('box_')]
    types = [k for k in df.columns if k.startswith('type_')]
    groups = [k for k in df.columns if k.startswith('group_')]
    columns += [c for s in zip(boxes, types, groups) for c in s]

    df = df[columns]

    # Write reconciled output along with training and test partitions of the data
    df.to_csv(args.reconciled, index=False)

    train_df, test_df = train_test_split(
        df, test_size=args.split, random_state=args.seed)

    name = args.reconciled / f'{args.reconciled.stem}.train.{args.reconciled.suffix}'
    train_df.to_csv(name, index=False)

    name = args.reconciled / f'{args.reconciled.stem}.test.{args.reconciled.suffix}'
    test_df.to_csv(name, index=False)


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
    Reconcile data from a Label Babel expedition.

    This script merges bounding boxes and label types from unreconciled Label Babel
    classifications. We have to figure out which bounding boxes refer to which labels
    on the herbarium sheet and then merge them to find a single "best" bounding box.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--unreconciled', required=True, type=Path,
        help="""The unreconciled input CSV.""")

    arg_parser.add_argument(
        '--reconciled', required=True, type=Path,
        help="""The reconciled output CSV.""")

    arg_parser.add_argument(
        '--image-dir', required=True, type=Path,
        help="""Read training images from this directory.""")

    arg_parser.add_argument(
        '--split', type=float, default=0.2,
        help="""Fraction of subjects in the test dataset. (default: %(default)s)""")

    arg_parser.add_argument(
        '--seed', type=int, help="""Create a random seed.""")

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    reconcile(ARGS)

    finished()
