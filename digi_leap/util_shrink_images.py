#!/usr/bin/env python3
import argparse
import mimetypes
import textwrap
import warnings
from pathlib import Path

from PIL import Image


def main():
    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    sheets = sorted(args.input_dir.glob("*.*"))

    for sheet_path in sheets:
        mime = mimetypes.guess_type(sheet_path)
        if mime[0] and mime[0].startswith("image"):
            shrink_sheet(sheet_path, args.output_dir, args.shrink_by)


def shrink_sheet(sheet_path, output_dir, shrink_by):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        with Image.open(sheet_path).convert("RGB") as image:
            dims = round(image.width / shrink_by), round(image.height / shrink_by)
            image = image.resize(dims)
            image.save(output_dir / sheet_path.name)


def parse_args():
    description = """This script shrinks images by a constant factor."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--input-dir",
        "-i",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Get input images from this directory.""",
    )

    arg_parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Output the shrunken images to this directory.""",
    )

    arg_parser.add_argument(
        "--shrink-by",
        "-s",
        type=float,
        metavar="FLOAT",
        default=2.0,
        help="""Shrink images by this factor. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
