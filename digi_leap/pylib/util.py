"""Common utilities for the project."""

import logging
import sqlite3
import sys
from contextlib import contextmanager
from os.path import basename, splitext
from random import choices, sample

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
    return DotDict({c[0]: row[i] for i, c in enumerate(cursor.description)})


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


def setup_logger():
    """Setup the logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def module_name() -> str:
    """Get the current module name."""
    return splitext(basename(sys.argv[0]))[0]


def started() -> None:
    """Log the program start time."""
    setup_logger()
    logging.info('=' * 80)
    logging.info(f'{module_name()} started')


def finished() -> None:
    """Log the program end time."""
    logging.info(f'{module_name()} finished')
