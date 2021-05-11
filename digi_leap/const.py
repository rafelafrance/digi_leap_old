"""Define literals used in the system."""

import os
from pathlib import Path

BATCH_SIZE = 1_000_000  # How many records to work with at a time

ROOT_DIR = Path('..' if os.getcwd().endswith('scratch') else '.')
DATA_DIR = ROOT_DIR / 'data'

IMAGE_DIR = DATA_DIR / 'images'
PROCESSED_DIR = DATA_DIR / 'processed'
RAW_DIR = DATA_DIR / 'raw'
TEMP_DIR = DATA_DIR / 'temp'

CSV_FILE = 'occurrence_raw.csv'
DB = PROCESSED_DIR / 'occurrence_raw_2021-02.sqlite3.db'

CHAR_BLACKLIST = '¥€£¢«»®©§{}|'
