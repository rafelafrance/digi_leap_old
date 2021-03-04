"""Common utilities for the project."""

from contextlib import contextmanager

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
