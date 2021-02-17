#!/usr/bin/env python3
"""Given a CSV file of iDigBio records, download the images."""

import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlretrieve

import pandas as pd
from tqdm import tqdm

from digi_leap.pylib.const import DATA_DIR


def download_idigbio(csv_path):
    """Download iDigBio images out of a CSV file."""
    target = 'dwc:associatedMedia'
    df = pd.read_csv(csv_path, dtype=str)

    images = df.loc[df[target].str.contains('http:')][target]

    for url in tqdm(images):
        fields = urlparse(url)
        name = f'{fields.netloc}_{fields.path}'
        name = re.sub(r'[^\w.]', '_', name)
        name = re.sub(r'__+', '_', name)
        name = re.sub(r'^_+|_+$', '', name)
        name += '.jpg' if not name.lower().endswith('.jpg') else ''
        path = DATA_DIR / 'images' / name
        if path.exists():
            continue
        try:
            urlretrieve(url, path)
        except HTTPError:
            continue


def fix_file_names(image_dir: Path):
    """Fix up file names."""
    paths = image_dir.glob('*')
    for src in tqdm(paths):
        dst = src.name
        dst = re.sub(r'[^\w.]', '_', dst)
        dst = re.sub(r'__+', '_', dst)
        dst = re.sub(r'^_+|_+$', '', dst)
        dst += '.jpg' if not dst.lower().endswith('.jpg') else ''
        dst = image_dir / dst
        if dst.name != src.name:
            src.rename(dst)


if __name__ == '__main__':
    download_idigbio(DATA_DIR / 'idb_image_url.csv')
    # fix_file_names(DATA_DIR / 'images')
