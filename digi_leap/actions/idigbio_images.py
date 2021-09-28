"""Given a CSV file of iDigBio records, download the images."""

import logging
import os
import sqlite3
from urllib.error import HTTPError
from urllib.request import urlretrieve

import pandas as pd
import tqdm
from PIL import Image, UnidentifiedImageError

import digi_leap.pylib.db as db


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


def verify_images(args):
    """Put valid image paths into a database."""
    images = []
    errors = []
    glob = args.sheets_dir.glob(args.glob)
    for path in tqdm.tqdm(glob):
        try:
            image = Image.open(path)
            _ = image.size  # This should be enough to see if it's valid
            images.append((str(path), ))
        except UnidentifiedImageError:
            logging.warning(f"{path} is not an image")
            errors.append((str(path), ))
            continue
        finally:
            image.close()

    with sqlite3.connect(args.database) as cxn:
        db.create_sheets_table(cxn)
        db.create_sheet_errors_table(cxn)
        db.insert_sheets_batch(cxn, images)
        db.insert_sheet_errors_batch(cxn, errors)
