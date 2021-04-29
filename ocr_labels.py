#!/usr/bin/env python
"""OCR  a set of labels."""

import logging
import textwrap
from argparse import ArgumentParser, Namespace
from os import makedirs
from pathlib import Path

from digi_leap.label import Label
from digi_leap.log import finished, started


def ocr_labels(args: Namespace) -> None:
    """OCR the label images."""
    make_dirs(args)

    label_paths = sorted(args.label_dir.glob('*'))
    for label_path in label_paths:
        logging.info(f'{label_path.stem}')

        label = prepare_image(label_path)

        output_label(label, args.data_dir, 'tsv')
        output_label(label, args.text_dir, 'txt')


def prepare_image(path):
    """Turn an image of a label into text."""
    label = Label(path)
    label.deskew()
    label.binarize()

    if lines := label.find_horizontal_lines(line_gap=5):
        label.remove_horiz_lines(lines, window=20, threshold=2)

    if lines := label.find_vertical_lines(line_gap=5):
        label.remove_vert_lines(lines, window=20, threshold=2)

    return label


def output_label(label, dir_, suffix):
    """Output data."""
    if dir_:
        info = label.ocr_data() if suffix == 'tsv' else label.ocr_text()
        path = dir_ / f'{label.path.stem}.{suffix}'
        with open(path, 'w') as out_file:
            out_file.write(info)
            out_file.write('\n')


def make_dirs(args):
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

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    ocr_labels(ARGS)

    finished()
