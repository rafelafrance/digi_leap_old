"""Define literals used in the system."""

import os
from pathlib import Path

BATCH_SIZE = 1_000_000  # How many records to work with at a time

ROOT_DIR = Path('..' if os.getcwd().endswith('notebooks') else '.')
DATA_DIR = ROOT_DIR / 'data'
TEMP_DIR = DATA_DIR / 'temp'

DUCK_DB = str(DATA_DIR / 'occurrence_raw_idigbio_2021-02.duckdb.db')

RAW_DB = str(DATA_DIR / 'occurrence_raw_idigbio_2021-02.sqlite3.db')
LABEL_DB = str(DATA_DIR / 'label_data.sqlite3.db')

ZIPPY = str(DATA_DIR / 'iDigBio_snapshot_2021-02.zip')
ZIP_FILE = 'occurrence_raw.csv'
