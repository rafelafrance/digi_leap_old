"""Define literals used in the system."""

from pathlib import Path

BATCH_SIZE = 1_000_000  # How many records to work with at a time

DATA_DIR = Path('.') / 'data'
TEMP_DIR = DATA_DIR / 'temp'
