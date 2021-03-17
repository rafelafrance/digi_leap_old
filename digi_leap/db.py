"""Common database functions."""
import sqlite3
from collections import defaultdict
from contextlib import contextmanager
from random import choices, sample

import duckdb

from digi_leap.util import DotDict


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


def get_labels(db, table, count):
    """Sample the label data so that we can update"""
    sql = f""" select * from {table} """

    with sqlite3.connect(db) as cxn:
        cxn.row_factory = dict_factory
        rows = [r for r in cxn.execute(sql).fetchall()]

    label_ids = list({r['label_id'] for r in rows})
    limit = count if count <= len(label_ids) else len(label_ids)
    label_ids = set(sample(label_ids, limit))

    labels = defaultdict(list)

    for row in rows:
        if row.label_id in label_ids:
            labels[row.label_id].append(row)

    return labels


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
