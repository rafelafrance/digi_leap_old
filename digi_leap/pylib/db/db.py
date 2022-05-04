"""Utilities for digi_leap.sqlite databases."""
import inspect
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from . import canned_sql


@contextmanager
def connect(db_path):
    """Add a row factory to the normal connection context manager."""
    try:
        with sqlite3.connect(db_path) as cxn:
            cxn.row_factory = sqlite3.Row
            yield cxn
    finally:
        pass


def execute(cxn, sql, params=None):
    """Execute a query -- Sugar for making database calls look similar."""
    params = params if params else []
    return cxn.execute(sql, params)


def canned_insert(table, cxn, batch):
    sql = canned_sql.CANNED_INSERTS[table]
    cxn.executemany(sql, batch)


def canned_select(key, cxn, **kwargs):
    sql = canned_sql.CANNED_SELECTS[key]
    args = kwargs if kwargs else None
    return cxn.execute(sql, tuple(args))


# ######################### runs table ################################################
def insert_run(cxn, args, comments: str = "") -> int:
    __, file, line, func, *_ = inspect.stack()[1]
    caller = f"file name: {Path(file).name}, function: {func}, line: {line}"

    json_args = json.dumps({k: str(v) for k, v in vars(args).items()})

    sql = """
        insert into runs ( caller,  args,  comments)
                  values (:caller, :args, :comments);
        """
    cxn.execute(sql, (caller, json_args, comments))
    results = cxn.execute("select seq from sqlite_sequence where name = 'runs';")

    return results.fetchone()[0]


def update_run_finished(cxn, run_id: int):
    sql = """
        update runs set finished = datetime('now', 'localtime') where run_id = ?
        """
    cxn.execute(sql, (run_id,))


def update_run_comments(cxn, run_id: int, comments: str):
    sql = """
        update runs set comments = ?, finished = datetime('now', 'localtime')
         where run_id = ?"""
    cxn.execute(sql, (comments, run_id))
