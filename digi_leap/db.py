"""Common database functions."""
import sqlite3
from collections import defaultdict
from random import sample

from junk.line import DotDict


def dict_factory(cursor, row):
    """Convert an SQLite3 query from a tuple to a dict."""
    return DotDict({c[0]: row[i] for i, c in enumerate(cursor.description)})


def get_labels(db, table, count):
    """Sample the label data so that we can update"""
    sql = f""" select * from {table} """

    with sqlite3.connect(db) as cxn:
        cxn.row_factory = dict_factory
        recs = [r for r in cxn.execute(sql).fetchall()]

    label_ids = sorted({r.label_id for r in recs})  # Sets do not use random.seed()
    limit = count if count <= len(label_ids) else len(label_ids)
    label_ids = set(sample(label_ids, limit))

    labels = defaultdict(list)

    for rec in recs:
        if rec.label_id in label_ids:
            labels[rec.label_id].append(rec)

    return list(labels.values())


def samples(db, table, k):
    """Choose imputations given values."""
    with sqlite3.connect(db) as cxn:
        cursor = cxn.execute(f'select * from {table}')
        defaults = [v[0] for v in cursor.fetchall()]
    k = k if k < len(defaults) else len(defaults)
    return sample(defaults, k)
