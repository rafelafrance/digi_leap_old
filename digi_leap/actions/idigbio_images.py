#!/usr/bin/env python3
"""Given a CSV file of iDigBio records, download the images."""

import re
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlretrieve

import pandas as pd
import tqdm


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
