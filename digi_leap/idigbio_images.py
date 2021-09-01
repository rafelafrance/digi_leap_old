#!/usr/bin/env python
"""Given a CSV file of iDigBio records, download the images."""

import argparse
import re
import textwrap
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlretrieve

import pandas as pd
import tqdm

from pylib.config import Config
import pylib.log as log


def download_idigbio(csv_path, image_dir):
    """Download iDigBio images out of a CSV file."""
    target = "dwc:associatedMedia"
    df = pd.read_csv(csv_path, dtype=str)

    images = df.loc[df[target].str.contains("http:")][target]

    for url in tqdm.tqdm(images):
        url_part = urlparse(url)
        name = f"{url_part.netloc}_{url_part.path}"
        name = re.sub(r"[^\w.]", "_", name)
        name = re.sub(r"__+", "_", name)
        name = re.sub(r"^_+|_+$", "", name)
        name += ".jpg" if not name.lower().endswith(".jpg") else ""
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
        should extract an iDigBio media file from a snapshot (step 01) before running
        this.
    """
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    defaults = Config().module_defaults()

    arg_parser.add_argument(
        "--database",
        default=defaults['database'],
        type=Path,
        help="""Path to the iDigBio database."""
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    # TODO: Use either a database from step 01 xor a CSV file
    # download_idigbio(CSV, IMAGE_DIR)

    log.finished()
