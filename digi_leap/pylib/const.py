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
CSV_FILE = f'{RAW_DATA}.csv'

REJECTS = [
    '',
    'illeg',
    'illegible text',
    'illegible',
    'locality illegible',
    'location not specified',
    'location undetermined',
    'location unknown',
    'location unspecified',
    'n/a',
    'na',
    'no additional data',
    'no additional information given',
    'no aplica',
    'no country on label',
    'no data',
    'no desc',
    'no details given',
    'no disponible',
    'no further data',
    'no further locality',
    'no information',
    'no loc',
    'no locality data',
    'no locality given',
    'no locality information provided on label',
    'no locality information provided on the label',
    'no locality information provided',
    'no locality information',
    'no locality or locality illegible',
    'no locality provided',
    'no locality',
    'no location data on label',
    'no precise loc',
    'no specific locality on sheet',
    'no specific locality recorded',
    'none given',
    'none',
    'not listed',
    'not on sheet',
    'not reported',
    'not seen',
    'not specified',
    'not stated',
    'null',
    'unknown',
    'unspecified',
    'without locality',
]
REJECT_VALUES = [f"'{v}'" for v in REJECTS]
REJECT_VALUES = ', '.join(REJECT_VALUES)
