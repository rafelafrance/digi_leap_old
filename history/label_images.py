#!/usr/bin/env python
"""Generate label images from the saved label text."""

import argparse
import textwrap
from os.path import join
from random import seed

from tqdm import tqdm

from digi_leap.db import get_labels
from history.digi_leap.font import choose_label_fonts
from history.digi_leap.label_image import LabelImage
from digi_leap.log import finished, started


def init_label_images(args) -> list[LabelImage]:
    """Get labels and format them."""
    labels = get_labels(args.database, args.input_table, args.count)
    return [LabelImage(recs) for recs in labels]


def layout(label):
    """Build the entire label from the text fragments."""
    label.layout()


def ransom_note(label):
    """Generate a label."""
    choose_label_fonts(label)
    layout(label)


def main(args):
    """Generate images."""
    if args.seed:
        seed(args.seed)

    labels = init_label_images(args)

    for label in tqdm(labels):
        ransom_note(label)

        name = join(args.y_dir, f'{label.label_id}.jpg')
        label.image_y.save(name, 'JPEG')


def parse_args():
    """Process command-line arguments."""
    description = """
        Generate label images from the saved label text.

        We can generate both normal and augmented images.
    """
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--database', '-d', required=True,
        help="""Path to the database.""")

    arg_parser.add_argument(
        '--input-table', '-i', default='labels',
        help=f"""Get data from this table. (default: %(default)s)""")

    arg_parser.add_argument(
        '--count', '-C', type=int, default=100_000,
        help=f"""The number of label images to generate. (default: %(default)s)""")

    arg_parser.add_argument(
        '--seed', '-S', type=int,
        help="""Create a random seed for python. (default: %(default)s)""")

    arg_parser.add_argument(
        '--x-dir', '-X',
        help="""Save un-augmented labels (Y) to this directory.""")

    arg_parser.add_argument(
        '--y-dir', '-Y',
        help="""Save augmented labels (X) to this directory.""")

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    main(ARGS)

    finished()
