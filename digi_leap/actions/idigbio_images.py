"""Given a CSV file of iDigBio records, download the images."""

import logging
import os
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
    for path in args.sheets_dir.glob(args.glob):
        image = None
        try:
            image = Image.open(path)
            width, height = image.size
            images.append({"path": str(path), "width": width, "height": height})
        except UnidentifiedImageError:
            logging.warning(f"{path} is not an image")
            errors.append({"path": str(path)})
        finally:
            if image:
                image.close()

    db.create_sheets_table(args.database)
    db.create_sheet_errors_table(args.database)
    db.insert_sheets(args.database, images)
    db.insert_sheet_errors(args.database, errors)
