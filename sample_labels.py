#!/usr/bin/env python
"""Output labels side-by-side with the OCRed text."""

import textwrap
from argparse import ArgumentParser, Namespace
from os import makedirs
from pathlib import Path
from random import sample

import matplotlib.pyplot as plt
from PIL import Image  # , ImageDraw, ImageFont
from tqdm import tqdm

from digi_leap.log import finished, started
from digi_leap.ocr import ocr_label
from digi_leap.ocr_score import score_easyocr


def sample_images(args):
    """Sample the images and output the OCR results."""
    make_dirs(args)

    paths = sorted(args.label_dir.glob("*.jpg"))
    samples = sample(paths, args.sample_size)
    for path in tqdm(samples):
        with Image.open(path) as image:
            tess = ocr_label(path)
            easy = ocr_label(path, score_easyocr)
            score = tess if tess.score > easy.score else easy

            fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(24, 10))
            fig.set_facecolor("white")

            ax1.axis("off")
            ax1.set_anchor("NE")
            ax1.imshow(image)

            # text = Image.new('RGB', image.size, color='white')
            # font = ImageFont.true type('fonts/print/Roboto/Roboto-Regular.ttf', 40)
            # draw = ImageDraw.Draw(text)
            # for item in score.score.data:
            #     draw.text(
            #         (item['left'], item['top']),
            #         item['text'], font=font, fill='black')

            ax2.axis("off")
            ax1.set_anchor("NW")
            ax2.text(
                0.0,
                1.0,
                score.score.text,
                verticalalignment="top",
                color="black",
                fontsize=16,
            )
            out_path = args.image_dir / path.name
            plt.savefig(out_path)


def make_dirs(args):
    """Create output directories."""
    if args.image_dir:
        makedirs(args.image_dir, exist_ok=True)


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
    Sample some labels, OCR them and output a 2-up image with the original label
    and its OCRed text.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--label-dir",
        "-l",
        required=True,
        type=Path,
        help="""The directory containing input labels.""",
    )

    arg_parser.add_argument(
        "--image-dir",
        "-i",
        required=True,
        type=Path,
        help="""Output the 2-up images to this directory.""",
    )

    arg_parser.add_argument(
        "--sample-size",
        "-s",
        type=int,
        default=100,
        help="""How many images to sample. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--seed", "-S", type=int, help="""Seed for the random number generator."""
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    sample_images(ARGS)

    finished()
