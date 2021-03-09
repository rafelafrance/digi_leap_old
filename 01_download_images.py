#!/usr/bin/env python
"""Given a CSV file of iDigBio records, download the images.

This script was used to get images for the Notes from Nature expedition for
finding labels. We will use the results from the expedition for training a
neural net to find labels and identify the type(s) of writing on them.

I originally got this list of images to download from a CSV file given
to me from an external source. I would now use the iDigBio snapshot to
do the same thing, and if we need more images I will. However, this will
require a rewrite.
"""

import re
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlretrieve

import pandas as pd
from tqdm import tqdm

from digi_leap.pylib.const import IMAGE_DIR, RAW_DIR
from digi_leap.pylib.util import ended, started

# Don't use this file in the future
OLD_CSV = 'idb_image_url.csv'


def download_idigbio(csv_path, image_dir):
    """Download iDigBio images out of a CSV file."""
    target = 'dwc:associatedMedia'
    df = pd.read_csv(csv_path, dtype=str)

    images = df.loc[df[target].str.contains('http:')][target]

    for url in tqdm(images):
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


if __name__ == '__main__':
    started()

    CSV = RAW_DIR / 'idb_image_url.csv'
    download_idigbio(CSV, IMAGE_DIR)

    ended()
