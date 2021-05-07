#!/usr/bin/env python
"""OCR  a set of labels.

Things to try:
    - Get label
    - Does OCR just work?
    - Will a simple spell correct fix things?
    - Is the label too small?
    - Do we need to orient the label? (90, 180, 270) (Use a simple CNN?)
    - Should we segment the label ourselves?
    - Are lines interfering with the OCR?
    - Is the contrast too low?
    - Will blurring help? or Sharpness?
    - Remove other noise? Blob removal
    - Will skew correction help?
    - Will binarizing help? sauvola otsu
    - Ensemble?

Methods for detecting text (ensemble):
    - Direct OCR?
    - Haar cascade?
    - HOG?
    - A simple CNN?
"""

import textwrap
from argparse import ArgumentParser, Namespace
from os import makedirs
from pathlib import Path
from typing import Optional

import numpy.typing as npt
from tqdm import tqdm
from skimage import io, color

from digi_leap.log import finished, started


def ocr_labels(args: Namespace) -> None:
    """OCR the label images."""
    make_dirs(args)

    label_paths = sorted(args.label_dir.glob('*'))
    for image_path in tqdm(label_paths):
        ...


def output_label(
        args: Namespace,
        image_path: Path,
        label: Optional[npt.ArrayLike],
        suffix: str,
) -> Optional[npt.ArrayLike]:
    """Output data in the specified format."""
    dir_ = args.data_dir if suffix == '.tsv' else args.text_dir
    if not dir_:
        return label

    path = dir_ / f'{image_path.stem}{suffix}'
    if path.exists() and not args.restart:
        return label

    if not label:
        label = prepare_image(image_path)

    info = label.ocr_data() if suffix == '.tsv' else label.ocr_text()
    info = info.strip()
    with open(path, 'w') as out_file:
        out_file.write(info)
        out_file.write('\n')

    return label


def prepare_image(path: Path) -> npt.ArrayLike:
    """Turn an image of a label into text."""
    label = io.imread(str(path))
    label = color.rgb2gray(label)
    # label.deskew()
    # label.binarize()
    #
    # if lines := label.find_horizontal_lines(line_gap=5):
    #     label.remove_horiz_lines(lines, window=20, threshold=2)
    #
    # if lines := label.find_vertical_lines(line_gap=5):
    #     label.remove_vert_lines(lines, window=20, threshold=2)

    return label


def make_dirs(args: Namespace) -> None:
    """Create output directories."""
    if args.data_dir:
        makedirs(args.data_dir, exist_ok=True)
    if args.text_dir:
        makedirs(args.text_dir, exist_ok=True)


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
    OCR images of labels.

    Take all images in the input --label-dir, OCR them and output the results
    to the --text-dir or --data-dir. The file name stems of the output files
    echo the file name stems of the input images. The input label images should
    be cut out of the images of the specimens first.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--label-dir', '-l', required=True, type=Path,
        help="""The directory containing input labels.""")

    arg_parser.add_argument(
        '--text-dir', '-t', type=Path,
        help="""The directory to output OCR text.""")

    arg_parser.add_argument(
        '--data-dir', '-d', type=Path,
        help="""The directory to output OCR data.""")

    arg_parser.add_argument(
        '--restart', action='store_true',
        help="""If selected this will overwrite existing output files.""")

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    ocr_labels(ARGS)

    finished()
