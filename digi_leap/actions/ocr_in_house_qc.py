"""Sample OCR and label detection for in-house quality control.

Sample reconciled herbarium sheets, mark the reconciled labels on those sheets,
get all of the ensemble labels for those sheets, score them, and output all of
the data for that sheet in a directory bundle.
"""

import json
import os
import random
import shutil
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

import digi_leap.pylib.ocr_results as results


def sample_sheets(args):
    """Sample the reconciled herbarium sheets and output the QC data."""
    qc_dir = str(args.qc_dir)
    if args.suffix:
        qc_dir += args.suffix
    qc_dir = Path(qc_dir)

    os.makedirs(qc_dir, exist_ok=True)

    image_files = [f for f in args.ensemble_image_dir.iterdir()]
    text_files = [f for f in args.ensemble_text_dir.iterdir()]

    with open(args.reconciled_jsonl) as jsonl_file:
        reconciled = [json.loads(ln) for ln in jsonl_file.readlines()]

    samples = random.sample(reconciled, args.sample_size)
    for sheet in samples:
        stem = Path(sheet["image_file"]).stem

        # Shorten file names
        name = stem
        name = name.replace("static_VascularPlant_originals_", "")
        name = name.replace("_format_large", "")
        name = name.replace("_http", "")

        sheet_dir = qc_dir / name
        os.makedirs(sheet_dir, exist_ok=True)

        output_herbarium_sheet(sheet, sheet_dir, args.sheets_dir)

        images = [f for f in image_files if f.stem.find(stem) >= 0]
        copy_label_images(images, sheet_dir)

        texts = [f for f in text_files if f.stem.find(stem) >= 0]
        score_label_text(texts, sheet_dir)

        with open(sheet_dir / "reconciled.json", "w") as json_file:
            json.dump(sheet, json_file, indent=2)


def score_label_text(texts, sheet_dir):
    """Return the scores for all of the predicted labels on the herbarium sheet."""
    scores = []
    for path in texts:
        parts = path.stem.split("_")
        score = {
            "index": int(parts[-2]),
            "type":  parts[-1],
        }
        with open(path) as text_file:
            text = text_file.read()
            words = text.split()
            count = len(words)

        if count == 0:
            score["hit_percent"] = 0
            score["word_count"] = 0
        else:
            hits = results.text_hits(text)
            score["hit_percent"] = round(100.0 * hits / count)
            score["word_count"] = count

        score["file_name"] = path.name  # Make this wide column last
        scores.append(score)

    scores = sorted(scores, key=lambda s: s["index"])
    df = pd.DataFrame(scores)
    df.to_csv(sheet_dir / "scores.csv", index=False)


def copy_label_images(images, sheet_dir):
    """Copy labels images into the QC directory."""
    for src in images:
        parts = src.stem.split("_")
        dst = sheet_dir / f"label_{parts[-2]}_{parts[-1]}.{src.suffix}"
        shutil.copy(src, dst)


def output_herbarium_sheet(sheet, sheet_dir, sheets_dir):
    """Get the herbarium sheet, draw reconciled bounding boxes, & output the image."""
    in_path = sheets_dir / sheet["image_file"]
    image = Image.open(in_path)
    draw = ImageDraw.Draw(image)
    for box in sheet["merged_boxes"]:
        draw.rectangle(box, outline="red", width=4)
    out_path = sheet_dir / f"herbarium_sheet.{in_path.suffix}"
    image.save(out_path)

# def parse_args() -> Namespace:
#     """Process command-line arguments."""
#     description = """
#         Build a single "best" label from the ensemble of OCR outputs.
#         """
#     arg_parser = ArgumentParser(
#         description=textwrap.dedent(description), fromfile_prefix_chars="@"
#     )
#
#     default = Config().module_defaults()
#
#     arg_parser.add_argument(
#         "--reconciled-jsonl",
#         default=default["reconciled_jsonl"],
#         type=Path,
#         help="""The JSONL file containing reconciled bounding boxes. The file
#             contains one reconciliation record per herbarium sheet.
#             (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--sheets-dir",
#         default=default["sheets_dir"],
#         type=Path,
#         help="""Images of herbarium sheets are in this directory
#              (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--ensemble-images",
#         default=default["ensemble_image_dir"],
#         type=Path,
#         help="""The directory containing the OCR ensemble images.
#              (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--ensemble-text",
#         default=default["ensemble_text_dir"],
#         type=Path,
#         help="""The directory containing the OCR ensemble text.
#              (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--qc-dir",
#         default=default["qc_dir"],
#         type=Path,
#         help="""Output the sampled QC data to this directory.
#              (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--sample-size",
#         type=int,
#         default=default["sample_size"],
#         help="""How many herbarium sheets to sample. (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--suffix",
#         help="""Add this to the end of the --qc-dir directory.""",
#     )
#
#     args = arg_parser.parse_args()
#     return args
#
#
# if __name__ == "__main__":
#     log.started()
#
#     ARGS = parse_args()
#     sample_sheets(ARGS)
#
#     log.finished()
