"""Define literals used in the system."""

import os
from pathlib import Path

BATCH_SIZE = 1_000_000  # How many records to work with at a time
LIMIT = 1_000_000

SEED = 9973

ROOT_DIR = Path('..' if os.getcwd().endswith('notebooks') else '.')
DATA_DIR = ROOT_DIR / 'data'

IMAGE_DIR = DATA_DIR / 'images'
PROCESSED_DIR = DATA_DIR / 'processed'
RAW_DIR = DATA_DIR / 'raw'
TEMP_DIR = DATA_DIR / 'temp'

CSV_FILE = 'occurrence_raw.csv'

with open(DATA_DIR / 'disallowed_values.txt') as in_file:
    DISALLOWED = [v.strip() for v in in_file.readlines() if v] + ['']
DISALLOWED_VALUES = [f"'{v}'" for v in DISALLOWED]
DISALLOWED_VALUES = ', '.join(DISALLOWED_VALUES)
