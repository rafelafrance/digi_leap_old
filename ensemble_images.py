#!/usr/bin/env python
"""Find "best" labels from ensembles of OCR results of each label."""

import os
import textwrap
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

import digi_leap.ocr_results as results
from digi_leap.const import FONTS_DIR
from digi_leap.log import finished, started
from digi_leap.ocr_rows import find_rows_of_text

FONT = FONTS_DIR / "print" / "Source_Code_Pro" / "SourceCodePro-Regular.ttf"
BASE_FONT_SIZE = 42

BATCH_SIZE = 10


class FontDict(dict):
    def __missing__(self, key):
        return ImageFont.truetype(str(FONT), key)


FONTS = FontDict()
BASE_FONT = ImageFont.truetype(str(FONT), BASE_FONT_SIZE)


def build_all_ensembles(args: Namespace) -> None:
    """Group OCR output paths by label."""
    os.makedirs(args.ensemble_dir, exist_ok=True)
    paths = group_files(args.ocr_dir, glob="*.csv")

    batches = [paths[i : i + BATCH_SIZE] for i in range(0, len(paths), BATCH_SIZE)]

    with Pool(processes=args.cpus) as pool, tqdm(total=len(batches)) as bar:
        results = [
            pool.apply_async(
                ensemble_batch, args=(vars(args), b), callback=lambda _: bar.update(1)
            )
            for b in batches
        ]
        _ = [r.get() for r in results]


def ensemble_batch(args, batch):
    """Find the "best" label on a batch of OCR results."""
    for path_tuple in batch:
        build_ensemble(args, path_tuple)


def build_ensemble(args, path_tuple):
    """Build the "best" label output given the ensemble of OCR results."""
    key, paths = path_tuple
    paths = [Path(p) for p in paths]

    label = Image.open(Path(args["label_dir"]) / f"{key}.jpg").convert("RGB")
    width, height = label.size
    recon = Image.new("RGB", label.size, color="white")

    df = get_boxes(paths)
    df = results.merge_bounding_boxes(df)
    df = find_rows_of_text(df)
    df = results.straighten_rows_of_text(df)

    draw_recon = ImageDraw.Draw(recon)

    df["font_size"] = BASE_FONT_SIZE

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

    path = Path(args["ensemble_dir"]) / f"{key}.jpg"
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
        """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--ocr-dir",
        required=True,
        type=Path,
        action="append",
        help="""The directory containing OCR output.""",
    )

    arg_parser.add_argument(
        "--label-dir",
        required=True,
        type=Path,
        help="""The directory containing images of labels.""",
    )

    arg_parser.add_argument(
        "--ensemble-dir",
        required=True,
        type=Path,
        help="""Output resulting images of the OCR ensembles to this directory.""",
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
        "--gutter",
        type=int,
        default=12,
        help="""Margin between lines of text in the reconstructed label output.
            (default %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    build_all_ensembles(ARGS)

    finished()
