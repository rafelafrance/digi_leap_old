"""Define literals used in the system."""

import os
from pathlib import Path

BATCH_SIZE = 1_000_000  # How many records to work with at a time
LIMIT = 1_000_000

ROOT_DIR = Path('..' if os.getcwd().endswith('notebooks') else '.')
DATA_DIR = ROOT_DIR / 'data'

IMAGE_DIR = DATA_DIR / 'images'
PROCESSED_DIR = DATA_DIR / 'processed'
RAW_DIR = DATA_DIR / 'raw'
TEMP_DIR = DATA_DIR / 'temp'
DEFAULT_DIR = DATA_DIR / 'default'

RAW_DATA = 'occurrence_raw'

RAW_DB = str(RAW_DIR / f'{RAW_DATA}_idigbio_2021-02.sqlite3.db')
LABEL_DB = str(PROCESSED_DIR / 'label_data.sqlite3.db')

ZIPPY = str(RAW_DIR / 'iDigBio_snapshot_2021-02.zip')
ZIP_FILE = f'{RAW_DATA}.csv'

# Default values
DEFAULT_FILES = {
    'columns': DEFAULT_DIR / 'columns.txt',
    'dates': DEFAULT_DIR / 'dates.txt',
    'names': DEFAULT_DIR / 'names.txt',
    'reject_values': DEFAULT_DIR / 'reject_values.txt',
    'rights_holders': DEFAULT_DIR / 'rights_holder.txt',
    'sex': DEFAULT_DIR / 'sexes.csv',
}
