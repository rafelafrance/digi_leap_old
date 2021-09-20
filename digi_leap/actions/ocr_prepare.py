#!/usr/bin/env python3
"""Prepare labels for OCR."""

import logging
import os
import textwrap
from argparse import ArgumentParser, Namespace
from itertools import chain
from multiprocessing import Pool
from os import makedirs
from os.path import basename, join
from pathlib import Path

import pandas as pd
import tqdm
from PIL import Image

import digi_leap.pylib.const as const
import digi_leap.pylib.label_transforms as trans
import digi_leap.pylib.log as log


def prepare_labels(args: Namespace) -> None:
    """Prepare the label images for OCR."""
    makedirs(args.prepared_label_dir, exist_ok=True)

    labels = filter_labels(args)
    labels = transform(labels, args)

    path = args.prepared_label_dir / "actions.csv"
    df = pd.DataFrame(labels)
    df.to_csv(path, index=False)


def filter_labels(args):
    """Filter labels that do not meet argument criteria."""
    logging.info("filtering labels")
    labels = sorted(args.label_dir.glob(args.image_filter))
    labels = [{"label": str(p)} for p in labels]
    labels = labels[: args.limit] if args.limit else labels
    return labels


def transform(labels, args):
    """Perform the label transformations before the OCR step(s)."""
    logging.info("transforming labels")

    batches = [
        labels[i : i + const.PROC_BATCH]
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

        path = join(args["prepared_label_dir"], basename(label["label"]))

        label["prepared"] = path
        label["actions"] = actions
        labels.append(label)

        image.save(path)

    return labels


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
        Prepare images of labels.

        Take all images in the --label-dir, prepare them for OCR and then
        write them to the --prepared-dir. The input label images should
        be cut out of the specimen images first.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--label-dir",
        required=True,
        type=Path,
        help="""The directory containing input labels.""",
    )

    arg_parser.add_argument(
        "--prepared-dir",
        required=True,
        type=Path,
        help="""Output transformed labels to this directory.""",
    )

    pipelines = list(trans.PIPELINES.keys())
    arg_parser.add_argument(
        "--pipeline",
        choices=pipelines,
        default=pipelines[0],
        help="""The pipeline to use for transformations. (default %(default)s)""",
    )

    cpus = max(1, min(10, os.cpu_count() - 4))
    arg_parser.add_argument(
        "--cpus",
        type=int,
        default=cpus,
        help="""How many CPUs to use. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many label images.""",
    )

    arg_parser.add_argument(
        "--image-filter",
        type=str,
        default="*.jpg",
        help="""Filter files in the --label-dir with this. (default %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    prepare_labels(ARGS)

    log.finished()
