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

import digi_leap.pylib.label_transforms as trans


def prepare_labels(args: Namespace) -> None:
    """Prepare the label images for OCR."""
    makedirs(args.output_dir, exist_ok=True)

    labels = filter_labels(args.label_dir, args.glob, args.limit)
    labels = transform(
        labels, args.cpus, args.batch_size, args.pipeline, args.output_dir
    )

    path = args.output_dir / "actions.csv"
    df = pd.DataFrame(labels)
    df.to_csv(path, index=False)


def filter_labels(label_dir, glob, limit):
    """Filter labels that do not meet argument criteria."""
    logging.info("filtering labels")
    labels = sorted(label_dir.glob(glob))
    labels = [{"label": str(p)} for p in labels]
    labels = labels[:limit] if limit else labels
    return labels


def transform(labels, cpus, batch_size, pipeline, output_dir):
    """Perform the label transformations before the OCR step(s)."""
    logging.info("transforming labels")

    batches = [labels[i : i + batch_size] for i in range(0, len(labels), batch_size)]

    with Pool(processes=cpus) as pool, tqdm.tqdm(total=len(labels)) as bar:
        results = [
            pool.apply_async(
                transform_batch,
                args=(b, pipeline, output_dir),
                callback=lambda _: bar.update(batch_size),
            )
            for b in batches
        ]
        results = [r.get() for r in results]

    labels = list(chain.from_iterable(results))
    return labels


def transform_batch(batch, pipeline, output_dir):
    """Perform the label transformations on a batch of labels."""
    labels = []
    for label in batch:
        image = Image.open(label["label"])

        image, actions = trans.transform_label(pipeline, image)

        path = join(output_dir, basename(label["label"]))

        label["prepared"] = path
        label["actions"] = actions
        labels.append(label)

        image.save(path)

    return labels
