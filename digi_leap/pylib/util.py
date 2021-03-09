"""Common utilities for the project."""

import csv
import sys
from os.path import basename, splitext
from contextlib import contextmanager
from datetime import datetime
from random import sample, choices

import duckdb

from digi_leap.pylib.const import DEFAULT_FILES, LIMIT


class DotDict(dict):
    """Allow dot.notation access to dictionary items."""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


@contextmanager
def duckdb_connect(db=':memory:'):
    """A context manager for a duck DB connection."""
    db = str(db)
    cxn = duckdb.connect(db)
    try:
        yield cxn
    finally:
        cxn.close()


def dict_factory(cursor, row):
    """Convert an SQLite3 query from a tuple to a dict."""
    return {c[0]: row[i] for i, c in enumerate(cursor.description)}


def sample_defaults(key, k=LIMIT):
    """Get a sample of default values."""
    values = []
    weights = []
    with open(DEFAULT_FILES[key]) as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            values.append(row['value'].strip())
            weights.append(int(row['weight']))
    return choices(values, weights, k=k)


def choose_defaults(key, k=LIMIT):
    """Choose defaults given values and a weights."""
    with open(DEFAULT_FILES[key]) as in_file:
        defaults = [v for ln in in_file.readlines() if (v := ln.strip())]
    k = k if k < len(defaults) else len(defaults)
    return sample(defaults, k)


def read_lines(key):
    """Read all lines from a default file."""
    with open(DEFAULT_FILES[key]) as in_file:
        defaults = [v for ln in in_file.readlines() if (v := ln.strip())]
    return defaults


def log(msg: str) -> None:
    """Log a status message."""
    print(f'{now()} {msg}')


def now() -> str:
    """Generate a timestamp."""
    return datetime.now().isoformat(sep=' ', timespec='seconds')


def today() -> str:
    """Get today's date."""
    return now()[:10]   # No day or month for time spec


def module_name() -> str:
    """Get the current module name."""
    return splitext(basename(sys.argv[0]))[0]


def started() -> None:
    """Log the program start time."""
    log('=' * 80)
    log(f'{module_name()} started')


def ended() -> None:
    """Log the program end time."""
    log(f'{module_name()} ended')
