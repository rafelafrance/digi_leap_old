#!/usr/bin/env python
"""Given a CSV file of iDigBio records, download the images."""

import argparse
import re
import textwrap
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlretrieve

import pandas as pd
import tqdm

import pylib.const as const
import pylib.log as log

# Don't use this file in the future
OLD_CSV = 'idb_image_url.csv'


def download_idigbio(csv_path, image_dir):
    """Download iDigBio images out of a CSV file."""
    target = 'dwc:associatedMedia'
    df = pd.read_csv(csv_path, dtype=str)

    images = df.loc[df[target].str.contains('http:')][target]

    for url in tqdm.tqdm(images):
        url_part = urlparse(url)
        name = f'{url_part.netloc}_{url_part.path}'
        name = re.sub(r'[^\w.]', '_', name)
        name = re.sub(r'__+', '_', name)
        name = re.sub(r'^_+|_+$', '', name)
        name += '.jpg' if not name.lower().endswith('.jpg') else ''
        path = image_dir / name
        if path.exists():
            continue
        try:
            urlretrieve(url, path)
        except HTTPError:
            continue


def parse_args():
    """Process command-line arguments."""
    description = """
    Use iDigBio records to download images.

    This script was used to get images for Notes from Nature expeditions for
    finding labels. We will use the results from the expedition for training a
    neural net to find labels and identify the type(s) of printing on them. You
    should extract an iDigBio media file from a snapshot (step 01) before running this.
    """
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--database', '-d', required=True,
        help="""Path to the database.""")

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    log.started()

    CSV = const.RAW_DIR / 'idb_image_url.csv'

    # TODO: Use either a database from step 01 xor a CSV file
    # download_idigbio(CSV, IMAGE_DIR)

    log.finished()
