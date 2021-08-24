#!/usr/bin/env python
"""Sample OCR and label detection for in-house quality control.

Sample reconciled herbarium sheets, mark the reconciled labels on those sheets,
get all of the ensemble labels for those sheets, score them, and output all of
the data for that sheet in a directory bundle.
"""

import json
import os
import random
import shutil
import textwrap
from argparse import ArgumentParser, Namespace
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

import pylib.const as const
import pylib.log as log
import pylib.ocr_results as results


def sample_sheets(args):
    """Sample the reconciled herbarium sheets and output the QC data."""
    os.makedirs(args.qc_dir, exist_ok=True)

    image_files = [f for f in args.ensemble_images.iterdir()]
    text_files = [f for f in args.ensemble_text.iterdir()]

    with open(args.reconciled_jsonl) as jsonl_file:
        reconciled = [json.loads(ln) for ln in jsonl_file.readlines()]

    samples = random.sample(reconciled, args.sample_size)
    for sheet in samples:
        stem = Path(sheet['image_file']).stem

        qc_dir = args.qc_dir / stem
        os.makedirs(qc_dir, exist_ok=True)

        output_herbarium_sheet(sheet, qc_dir, args.sheets_dir)

        images = [f for f in image_files if f.stem.find(stem) >= 0]
        copy_label_images(images, qc_dir)

        texts = [f for f in text_files if f.stem.find(stem) >= 0]
        score_label_text(texts, qc_dir)

        with open(qc_dir / 'reconciled.json', 'w') as json_file:
            json.dump(sheet, json_file, indent=2)


def score_label_text(texts, qc_dir):
    """Return the scores for all of the predicted labels on the herbarium sheet."""
    scores = []
    for path in texts:
        parts = path.stem.split('_')
        score = {
            'index': int(parts[-2]),
            'type': parts[-1],
        }
        with open(path) as text_file:
            text = text_file.read()
            words = text.split()
            count = len(words)

        if count == 0:
            score['hit_percent'] = 0.0
            score['word_count'] = 0
        else:
            hits = results.text_hits(text)
            score['hit_percent'] = round(100.0 * hits / count)
            score['word_count'] = count

        score['file_name'] = path.name  # Make this wide column last
        scores.append(score)

    scores = sorted(scores, key=lambda s: s['index'])
    df = pd.DataFrame(scores)
    df.to_csv(qc_dir / 'scores.csv', index=False)


def copy_label_images(images, qc_dir):
    """Copy labels images into the QC directory."""
    for src in images:
        dst = qc_dir / src.name
        shutil.copy(src, dst)


def output_herbarium_sheet(sheet, qc_dir, sheets_dir):
    """Get the herbarium sheet, draw reconciled bounding boxes, & output the image."""
    in_path = sheets_dir / sheet["image_file"]
    image = Image.open(in_path)
    draw = ImageDraw.Draw(image)
    for box in sheet["merged_boxes"]:
        draw.rectangle(box, outline='red', width=4)
    out_path = qc_dir / sheet["image_file"]
    image.save(out_path)


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
        Build a single "best" label from the ensemble of OCR outputs.
        """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    defaults = const.get_config()

    arg_parser.add_argument(
        "--reconciled-jsonl",
        default=defaults['reconciled_jsonl'],
        type=Path,
        help="""The JSONL file containing reconciled bounding boxes. The file
            contains one reconciliation record per herbarium sheet.
            (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--sheets-dir",
        default=defaults['sheets_dir'],
        type=Path,
        help="""Images of herbarium sheets are in this directory
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--ensemble-images",
        default=defaults['ensemble_images'],
        type=Path,
        help="""The directory containing the OCR ensemble images.
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--ensemble-text",
        default=defaults['ensemble_text'],
        type=Path,
        help="""The directory containing the OCR ensemble text.
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--qc-dir",
        default=defaults['qc_dir'],
        type=Path,
        help="""Output the sampled QC data to this directory.
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--sample-size",
        type=int,
        default=defaults['sample_size'],
        help="""How many herbarium sheets to sample. (default %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    sample_sheets(ARGS)

    log.finished()
