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

from digi_leap.pylib.ocr_results import text_hits


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

    sheets = get_sheets(args.ensemble_images, args.ensemble_text, args.label_dir)

    sheets = filter_labels_by_words(
        sheets, args.word_count_threshold, args.vocab_count_threshold
    )

    sheets = sort_sheet_labels(sheets)

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


def filter_labels_by_words(sheets, word_threshold, vocab_threshold):
    """Filter labels by word count and vocabulary hit count."""
    for name, labels in sheets.items():
        if not labels:
            continue

        new_labels = []

        for label in labels:
            with open(label.text) as text_file:
                text = text_file.read()
                words = text.split()

                # Skip labels with too few words
                if len(words) < word_threshold:
                    continue

                # Skip labels with too few vocab hits
                hits = text_hits(text)
                if hits < vocab_threshold:
                    continue

            new_labels.append(label)

        sheets[name] = new_labels

    return sheets


def sort_sheet_labels(sheets):
    """Sort each sheet's labels by image size [descending]."""
    for name, labels in sheets.items():
        if not labels:
            continue

        # Sort by image size
        for label in labels:
            label.size = label.raw.stat().st_size
        sheets[name] = sorted(labels, key=lambda x: -x.size)

    return sheets


def get_sheets(ensemble_images, ensemble_text, label_dir):
    """Build a dictionary of expedition sheets with lists of their labels."""
    images = ensemble_images.glob("*.jpg")
    texts = ensemble_text.glob("*.txt")

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
