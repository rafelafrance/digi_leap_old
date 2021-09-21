#!/usr/bin/env python3
"""Prepare labels for OCR."""

import logging
from argparse import Namespace
from itertools import chain
from multiprocessing import Pool
from os import makedirs
from os.path import basename, join

import pandas as pd
import tqdm
from PIL import Image

import digi_leap.pylib.const as const
import digi_leap.pylib.label_transforms as trans


def prepare_labels(args: Namespace) -> None:
    """Prepare the label images for OCR."""
    makedirs(args.output_dir, exist_ok=True)

    labels = filter_labels(args)
    labels = transform(labels, args)

    path = args.output_dir / "actions.csv"
    df = pd.DataFrame(labels)
    df.to_csv(path, index=False)


def filter_labels(args):
    """Filter labels that do not meet argument criteria."""
    logging.info("filtering labels")
    labels = sorted(args.label_dir.glob(args.glob))
    labels = [{"label": str(p)} for p in labels]
    labels = labels[: args.limit] if args.limit else labels
    return labels


def transform(labels, args):
    """Perform the label transformations before the OCR step(s)."""
    logging.info("transforming labels")

    batches = [
        labels[i: i + const.PROC_BATCH]
        for i in range(0, len(labels), const.PROC_BATCH)
    ]

    with Pool(processes=args.cpus) as pool, tqdm.tqdm(total=len(batches)) as bar:
        results = [
            pool.apply_async(
                transform_batch, args=(b, vars(args)), callback=lambda _: bar.update()
            )
            for b in batches
        ]
        results = [r.get() for r in results]

    labels = list(chain.from_iterable(results))
    return labels


def transform_batch(batch, args):
    """Perform the label transformations on a batch of labels."""
    labels = []
    for label in batch:
        image = Image.open(label["label"])

        image, actions = trans.transform_label(args["pipeline"], image)

        path = join(args["output_dir"], basename(label["label"]))

        label["prepared"] = path
        label["actions"] = actions
        labels.append(label)

        image.save(path)

    return labels
