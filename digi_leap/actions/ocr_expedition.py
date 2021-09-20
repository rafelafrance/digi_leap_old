#!/usr/bin/env python3
"""Build an expedition for scoring OCR output."""

import logging
from argparse import Namespace
from collections import defaultdict
from dataclasses import dataclass
from os import makedirs
from pathlib import Path
from shutil import copyfile
from typing import Optional

import pandas as pd
from PIL import Image

import digi_leap.pylib.log as log
from digi_leap.pylib.args import ArgParser


@dataclass
class Label:
    """Holds information for a particular label."""

    image: Optional[Path] = None  # Ensemble generated image
    text: Optional[Path] = None  # Ensemble generated text
    raw: Optional[Path] = None  # Original cropped label
    type_: str = ""  # Label type
    size: int = 0


def build_expedition(args: Namespace) -> None:
    """Group OCR output paths by label."""
    makedirs(args.expedition_dir, exist_ok=True)

    sheets = get_sheets(args.ensemble_image_dir, args.ensemble_text_dir, args.label_dir)
    sheets = sort_sheet_labels(sheets, args.word_threshold)

    # The order of the following 3 filters matters
    # Remove rulers before getting the largest labels
    # Get largest labels before filtering by label type
    if args.filter_rulers > 0.0:
        sheets = filter_rulers(sheets, args.filter_rulers)

    if args.largest_labels > 0:
        sheets = take_n_largest(sheets, args.largest_labels)

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


def take_n_largest(sheets, n):
    """Keep the n largest labels."""
    # They're already sorted
    return {name: labels[:n] for name, labels in sheets.items()}


def filter_rulers(sheets, threshold):
    """Remove rulers from each herbarium sheet."""
    for name, labels in sheets.items():
        new_labels = []
        for label in labels:
            if not label.raw.exists():
                logging.warning(f"Could not open {label.raw}")
                continue
            with Image.open(label.raw) as image:
                width, height = image.size
            if (width / height) <= threshold and (height / width) <= threshold:
                new_labels.append(label)
        sheets[name] = new_labels
    return sheets


def sort_sheet_labels(sheets, word_threshold):
    """Sort each sheet's labels by word count [descending]."""
    for name, labels in sheets.items():
        if not labels:
            continue

        # Sort by word count
        for label in labels:
            with open(label.text) as text_file:
                text = text_file.read()
                words = text.split()
                label.size = len(words)
        labels = sorted(labels, key=lambda x: -x.size)

        # Check word count
        if labels[0].size >= word_threshold:
            sheets[name] = labels
            continue

        # Sort by image size
        for label in labels:
            label.size = label.raw.stat().st_size
        sheets[name] = sorted(labels, key=lambda x: -x.size)

    return sheets


def get_sheets(ensemble_image_dir, ensemble_text_dir, label_dir):
    """Build a dictionary of expedition sheets with lists of their labels."""
    images = ensemble_image_dir.glob("*.jpg")
    texts = ensemble_text_dir.glob("*.txt")

    # Create a dict of labels
    ensemble_labels = defaultdict(Label)
    for image in images:
        ensemble_labels[image.stem].image = image
        ensemble_labels[image.stem].type_ = image.stem.split("_")[-1]
        ensemble_labels[image.stem].raw = label_dir / image.name

    for text in texts:
        ensemble_labels[text.stem].text = text

    # Merge labels by herbarium sheet
    sheets = defaultdict(list)
    for key, label in ensemble_labels.items():
        name = " ".join(key.split("_")[:-2])
        sheets[name].append(label)

    return sheets


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """Build build an expedition from OCR ensemble output."""
    parser = ArgParser(description)

    parser.ensemble_image_dir()
    parser.ensemble_text_dir()
    parser.expedition_dir()
    parser.label_dir(action="read")
    parser.filter_rulers()
    parser.largest_labels()
    parser.filter_types()
    parser.word_threshold()
    parser.limit()

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    build_expedition(ARGS)

    log.finished()
