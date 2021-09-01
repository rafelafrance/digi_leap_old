#!/usr/bin/env python
"""Build an expedition for scoring OCR output."""

import logging
import textwrap
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from collections import defaultdict
from dataclasses import dataclass
from os import makedirs
from pathlib import Path
from shutil import copyfile
from typing import Optional

import pandas as pd
from PIL import Image

import pylib.log as log
import pylib.subject as subject
from pylib.config import Config


@dataclass
class Label:
    """Holds the image path and text path for a particular label."""

    image: Optional[Path] = None
    text: Optional[Path] = None
    type_: str = ""
    size: int = 0


def build_expedition(args: Namespace) -> None:
    """Group OCR output paths by label."""
    makedirs(args.expedition_dir, exist_ok=True)

    sheets = get_sheets(args.ensemble_image_dir, args.ensemble_text_dir)
    sheets = sort_sheet_labels(sheets)

    # The order of the following 3 filters matters
    # Remove rulers before getting the largest labels
    # Get largest labels before filtering by label type
    if args.filter_rulers > 0.0:
        sheets = filter_rulers(sheets, args.filter_rulers, args.prepared_label_dir)

    if args.largest_labels > 0:
        sheets = largest_labels(sheets, args.largest_labels)

    if args.filter_types:
        sheets = filter_types(sheets, args.filter_types)

    write_expedition(sheets, args.expedition_dir)


def write_expedition(sheets, expedition_dir):
    """Output the expedition images and manifest."""
    manifest = []
    for name, labels in sheets.items():
        for label in labels:
            src = label.image
            dst = expedition_dir / src.name
            copyfile(src, dst)
            manifest.append(src.name)
    df = pd.DataFrame(data=manifest, columns=["label"])
    df.to_csv(expedition_dir / "manifest.csv", index=False)


def filter_types(sheets, types):
    """Remove labels with the given types."""
    return {
        nm: [lb for lb in lbs if lb.type_ not in types] for nm, lbs in sheets.items()
    }


def largest_labels(sheets, n):
    """Keep the n largest labels."""
    # They're already sorted by word count
    return {name: labels[:n] for name, labels in sheets.items()}


def filter_rulers(sheets, threshold, prepared_label_dir):
    """Remove rulers from each herbarium sheet."""
    for name, labels in sheets.items():
        new_labels = []
        for label in labels:
            path = prepared_label_dir / label.image.name
            if not path.exists():
                logging.warning(f"Could not open {path}")
                continue
            with Image.open(path) as image:
                width, height = image.size
            if (width / height) <= threshold and (height / width) <= threshold:
                new_labels.append(label)
        sheets[name] = new_labels
    return sheets


def sort_sheet_labels(sheets):
    """Sort each sheet's labels by word count [descending]."""
    for name, labels in sheets.items():
        for label in labels:
            label.size = label.text.stat().st_size
        sheets[name] = sorted(labels, key=lambda x: -x.size)
    return sheets


def get_sheets(ensemble_image_dir, ensemble_text_dir):
    """Build a dictionary of expedition sheets with lists of their labels."""
    images = ensemble_image_dir.glob("*.jpg")
    texts = ensemble_text_dir.glob("*.txt")

    ensemble_labels = defaultdict(Label)
    for image in images:
        ensemble_labels[image.stem].image = image
        ensemble_labels[image.stem].type_ = image.stem.split("_")[-1]
    for text in texts:
        ensemble_labels[text.stem].text = text

    sheets = defaultdict(list)
    for key, label in ensemble_labels.items():
        name = " ".join(key.split("_")[:-2])
        sheets[name].append(label)

    return sheets


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """Build build an expedition from OCR ensemble output."""
    arg_parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=textwrap.dedent(description),
        fromfile_prefix_chars="@",
    )

    configs = Config()
    defaults = configs.module_defaults()

    arg_parser.add_argument(
        "--ensemble-image-dir",
        default=defaults["ensemble_image_dir"],
        type=Path,
        help="""Get images of the OCR ensembles results from this directory.
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--ensemble-text-dir",
        default=defaults["ensemble_text_dir"],
        type=Path,
        help="""Get text of the OCR ensembles results from this directory.
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--expedition-dir",
        default=defaults["expedition_dir"],
        type=Path,
        help="""Get text of the OCR ensembles results from this directory.
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--prepared-label-dir",
        default=defaults["prep_deskew_dir"],
        type=Path,
        help="""The directory containing images of labels ready for OCR. This is only
            needed if you are filtering out rulers. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--filter-rulers",
        default=defaults["filter_rulers"],
        type=float,
        help="""Remove rulers where the side ratio is greater than the given threshold.
        (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--largest-labels",
        default=defaults["largest_labels"],
        type=int,
        help="""Keep the N labels with the highest word count. (default %(default)s)""",
    )

    default = " ".join(configs.default_list("filter_types"))
    choices = subject.CLASSES
    arg_parser.add_argument(
        "--filter-types",
        choices=choices,
        default=default,
        help="""Remove these types of labels. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many label images.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    build_expedition(ARGS)

    log.finished()
