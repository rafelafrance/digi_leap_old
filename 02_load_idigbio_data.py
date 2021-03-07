#!/usr/bin/env python
"""Load iDigBio Data for Label Text Generation.

The files in the iDigBio snapshot are just too big to work with. So, we
extract some data from them and use that for generating fake labels.
"""

import re
import sqlite3
import zipfile

import pandas as pd
from tqdm import tqdm

from digi_leap.pylib.const import BATCH_SIZE, RAW_DB, ZIPPY, ZIP_FILE


def get_headers(zippy, zip_file):
    """Get the headers from the CSV file in the zipped snapshot."""
    with zipfile.ZipFile(zippy) as zippy:
        with zippy.open(zip_file) as in_file:
            headers = in_file.readline()
    return [h.decode().strip() for h in sorted(headers.split(b','))]


def get_columns(headers):
    """Convert the CSV column names into something easily usable by SQLite3."""
    # These are names that SQL will not like
    bad_names = """ group order references """.split()

    columns = {}
    used = set()

    for head in headers:
        col = head.split(':')[-1]
        col = re.sub(r'(?<![A-Z])([A-Z])', r'_\1', col).lower()
        col = re.sub(r'^_', '', col)
        if col in used:
            col = head.replace(':', '_')
            col = re.sub(r'(?<![A-Z])([A-Z])', r'_\1', col).lower()
            col = re.sub(r'^_', '', col)
        if col in bad_names:
            col += '_'
        columns[head] = col
        used.add(col)
    return columns


def insert(zippy, zip_file, raw_db, batch_size, columns):
    """Insert data from the CSV file into an SQLite3 database."""
    table = zip_file.split('.')[0]

    with sqlite3.connect(raw_db) as cxn:
        with zipfile.ZipFile(zippy) as zipped:
            with zipped.open(zip_file) as in_file:

                reader = pd.read_csv(
                    in_file, dtype=str, keep_default_na=False, chunksize=batch_size)

                if_exists = 'replace'

                for df in tqdm(reader):
                    df = df.rename(columns=columns)

                    df.to_sql(table, cxn, if_exists=if_exists, index=False)

                    if_exists = 'append'


def load_data(zippy, zip_file, raw_db, batch_size):
    """Load the data."""
    headers = get_headers(zippy, zip_file)
    columns = get_columns(headers)
    insert(zippy, zip_file, raw_db, batch_size, columns)


if __name__ == '__main__':
    load_data(ZIPPY, ZIP_FILE, RAW_DB, BATCH_SIZE)
