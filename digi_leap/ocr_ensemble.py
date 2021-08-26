#!/usr/bin/env python
"""Find "best" labels from ensembles of OCR results of each label."""

import os
import textwrap
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
import tqdm
from PIL import Image, ImageDraw, ImageFont

import pylib.const as const
import pylib.log as log
import pylib.ocr_results as results
import pylib.ocr_rows as rows

FONT = const.FONTS_DIR / "print" / "Source_Code_Pro" / "SourceCodePro-Regular.ttf"
BASE_FONT_SIZE = 42


class FontDict(dict):
    """Allow easy resizing of fonts."""

    def __missing__(self, key):
        return ImageFont.truetype(str(FONT), key)


FONTS = FontDict()
BASE_FONT = ImageFont.truetype(str(FONT), BASE_FONT_SIZE)


def build_all_ensembles(args: Namespace) -> None:
    """Group OCR output paths by label."""
    if args.ensemble_images:
        os.makedirs(args.ensemble_images, exist_ok=True)
    if args.ensemble_text:
        os.makedirs(args.ensemble_text, exist_ok=True)

    paths = group_files(args.ocr_dir)
    paths = paths[: args.limit] if args.limit else paths

    batches = [
        paths[i : i + const.PROC_BATCH] for i in range(0, len(paths), const.PROC_BATCH)
    ]

    arg_dict = vars(args)

    with Pool(processes=args.cpus) as pool, tqdm.tqdm(total=len(batches)) as bar:
        all_results = [
            pool.apply_async(
                ensemble_batch, args=(arg_dict, b), callback=lambda _: bar.update()
            )
            for b in batches
        ]
        _ = [r.get() for r in all_results]


def ensemble_batch(args, batch):
    """Find the "best" label on a batch of OCR results."""
    for path_tuple in batch:
        build_ensemble(args, path_tuple)


def build_ensemble(args, path_tuple):
    """Build the "best" label output given the ensemble of OCR results."""
    stem, paths = path_tuple
    paths = [Path(p) for p in paths]

    df = get_boxes(paths)
    if df.shape[0] == 0:
        return

    df = results.merge_bounding_boxes(df)
    df = rows.find_rows_of_text(df)

    if args.get("ensemble_text"):
        build_ensemble_text(args, stem, df)

    if args.get("ensemble_images"):
        build_ensemble_images(args, stem, df)


def build_ensemble_text(args, stem, df):
    """Build the "best" text output given the ensemble of OCR results."""
    lines = [" ".join(b.text) + "\n" for _, b in df.groupby("row")]
    path = Path(args["ensemble_text"]) / f"{stem}.txt"
    with open(path, "w") as out_file:
        out_file.writelines(lines)


def build_ensemble_images(args, stem, df):
    """Build the "best" image output given the ensemble of OCR results."""
    label = Image.open(Path(args["label_dir"]) / f"{stem}.jpg").convert("RGB")
    width, height = label.size
    recon = Image.new("RGB", label.size, color="white")

    draw_recon = ImageDraw.Draw(recon)

    df = results.straighten_rows_of_text(df)
    df["font_size"] = BASE_FONT_SIZE

    font_size, text_right, text_bottom = None, None, None
    for idx, box in df.iterrows():
        for font_size in range(BASE_FONT_SIZE, 16, -1):
            text_left, text_top, text_right, text_bottom = draw_recon.textbbox(
                (box.left, box.top), box.text, font=FONTS[font_size], anchor="lt"
            )
            if box.right >= text_right and box.bottom >= text_bottom:
                break
        df.at[idx, "font_size"] = int(font_size)
        df.at[idx, "right"] = text_right
        df.at[idx, "bottom"] = text_bottom

    df = results.arrange_rows_of_text(df)
    recon_bottom = df.new_bottom.max()

    for _, box in df.iterrows():
        draw_recon.text(
            (box.new_left, box.new_top),
            box.text,
            font=FONTS[box.font_size],
            fill="black",
            anchor="lt",
        )

    recon_bottom += args["gutter"]
    recon = recon.crop((0, 0, recon.width, recon_bottom))

    image = Image.new("RGB", (width, height + recon_bottom))
    image.paste(label, (0, 0))
    image.paste(recon, (0, height))

    path = Path(args["ensemble_images"]) / f"{stem}.jpg"
    image.save(path)


def group_files(
    ocr_dirs: list[Path], glob: str = "*.csv"
) -> list[tuple[str, list[Path]]]:
    """Find files that represent then same label and group them."""
    path_dict = defaultdict(list)
    for ocr_dir in ocr_dirs:
        paths = ocr_dir.glob(glob)
        for path in paths:
            label = path.stem
            path_dict[label].append(str(path))
    path_tuples = [(k, v) for k, v in path_dict.items()]
    path_tuples = sorted(path_tuples, key=lambda p: p[0])
    return path_tuples


def get_boxes(paths):
    """Get all the bounding boxes from the ensemble."""
    boxes = []
    for path in paths:
        df = results.get_results_df(path)
        boxes.append(df)
    return pd.concat(boxes)


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
        Build a single "best" label from the ensemble of OCR outputs.

        An ensemble is a list of OCR outputs with the same name contained
        in parallel directories. For instance, if you have OCR output
        (from ocr_labels.py) for three different runs then an ensemble
        will be:
            output/ocr/run1/label1.csv
            output/ocr/run2/label1.csv
            output/ocr/run3/label1.csv
        """
    arg_parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=textwrap.dedent(description),
        fromfile_prefix_chars="@",
    )

    defaults = const.get_config()

    arg_parser.add_argument(
        "--ocr-dir",
        default=defaults["ocr_dir"],
        action="append",
        help="""A directory that contains OCR output in CSV form. You may use
            wildcards and/or use this option more than once. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--label-dir",
        default=defaults["label_dir"],
        type=Path,
        help="""The directory containing images of labels. NOTE: This should contain
            images that have gone through (at least) some of the transforms. I.e. The
            label images should be scaled, oriented, deskewed. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--ensemble-images",
        default=defaults["ensemble_images"],
        type=Path,
        help="""Output resulting images of the OCR ensembles to this directory.
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--ensemble-text",
        default=defaults["ensemble_text"],
        type=Path,
        help="""Output resulting text of the OCR ensembles to this directory.
             (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--cpus",
        default=defaults["cpus"],
        type=int,
        help="""How many CPUs to use. (default %(default)s)""",
    )

    arg_parser.add_argument(
        "--gutter",
        type=int,
        default=defaults["gutter"],
        help="""Margin between lines of text in the reconstructed label output.
            (default %(default)s)""",
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
    build_all_ensembles(ARGS)

    log.finished()
