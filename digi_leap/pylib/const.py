"""Define literals used in the system."""

import os
from pathlib import Path

BATCH_SIZE = 1_000_000  # How many records to work with at a time
RAW_DATA_COUNT = 100_000  # This should be enough for training

ROOT_DIR = Path('..' if os.getcwd().endswith('notebooks') else '.')
DATA_DIR = ROOT_DIR / 'data'

IMAGE_DIR = DATA_DIR / 'images'
PROCESSED_DIR = DATA_DIR / 'processed'
RAW_DIR = DATA_DIR / 'raw'
TEMP_DIR = DATA_DIR / 'temp'

RAW_DATA = 'occurrence_raw'

RAW_DB = str(RAW_DIR / f'{RAW_DATA}_idigbio_2021-02.sqlite3.db')
LABEL_DB = str(PROCESSED_DIR / f'{RAW_DATA}.sqlite3.db')

ZIPPY = str(RAW_DIR / 'iDigBio_snapshot_2021-02.zip')
ZIP_FILE = f'{RAW_DATA}.csv'
