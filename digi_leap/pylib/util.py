"""Common utilities for the project."""

import sqlite3
import sys
from os.path import basename, splitext
from contextlib import contextmanager
from datetime import datetime
from random import sample, choices

import duckdb


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


def choose_values(db, table, k):
    """Get a sample of imputations given a set of values and weights."""
    with sqlite3.connect(db) as cxn:
        cursor = cxn.execute(f'select * from {table}')
        rows = cursor.fetchall()
        values = [r[0].strip() for r in rows]
        weights = [int(r[1]) for r in rows]
    return choices(values, weights, k=k)


def sample_values(db, table, k):
    """Choose imputations given values."""
    with sqlite3.connect(db) as cxn:
        cursor = cxn.execute(f'select * from {table}')
        defaults = [v[0] for v in cursor.fetchall()]
    k = k if k < len(defaults) else len(defaults)
    return sample(defaults, k)


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
