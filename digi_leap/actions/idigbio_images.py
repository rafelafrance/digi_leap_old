"""Given a CSV file of iDigBio records, download the images."""

import os
from urllib.error import HTTPError
from urllib.request import urlretrieve

import pandas as pd
import tqdm


def download_images(args):
    """Download iDigBio images out of a CSV file."""
    os.makedirs(args.sheets_dir, exist_ok=True)

    df = pd.read_csv(args.csv_file, index_col="coreid", dtype=str)
    if args.sample_size > 0:
        df = df.sample(args.sample_size)

    for coreid, row in tqdm.tqdm(df.iterrows()):
        path = args.sheets_dir / f"{coreid}.jpg"
        if path.exists():
            continue
        try:
            urlretrieve(row[args.url_column], path)
        except HTTPError:
            continue
