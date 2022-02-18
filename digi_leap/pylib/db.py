"""Utilities for digi_leap.sqlite databases."""
import re
import sqlite3
import sys
from pathlib import Path
from typing import Optional
from typing import Union

DbPath = Union[Path, str]


def build_select(sql: str, *, limit: int = 0, **kwargs) -> tuple[str, list]:
    """Select records given a base SQL statement and keyword parameters."""
    sql, params = build_where(sql, **kwargs)

    if limit:
        sql += " limit ?"
        params.append(limit)

    return sql, params


def build_where(sql: str, **kwargs) -> tuple[str, list]:
    """Build a simple-mined where clause."""
    params, where = [], []

    for key, value in kwargs.items():
        key = key.strip("_")
        if value is None:
            pass
        elif isinstance(value, list) and value:
            where.append(f"{key} in ({','.join(['?'] * len(value))})")
            params += value
        else:
            where.append(f"{key} = ?")
            params.append(value)

    sql += (" where " + " and ".join(where)) if where else ""
    return sql, params


def rows_as_dicts(database: DbPath, sql: str, params: Optional[list] = None):
    """Convert the SQL execute cursor to a list of dicts."""
    params = params if params else []
    with sqlite3.connect(database) as cxn:
        cxn.row_factory = sqlite3.Row
        rows = [dict(r) for r in cxn.execute(sql, params)]
    return rows


def insert_batch(database: DbPath, sql: str, batch: list) -> None:
    """Insert a batch of sheets records."""
    if batch:
        with sqlite3.connect(database) as cxn:
            cxn.executemany(sql, batch)


def create_table(database: DbPath, sql: str, *, drop: bool = False) -> None:
    """Create a table."""
    flags = re.IGNORECASE | re.VERBOSE
    match = re.search(r" if \s+ not \s+ exists \s+ (\w+) ", sql, flags=flags)

    if not match:
        sys.exit(f"Could not parse create table for '{sql}'")

    table = match.group(1)

    with sqlite3.connect(database) as cxn:
        if drop:
            cxn.executescript(f"""drop table if exists {table};""")

        cxn.executescript(sql)


# ############## Vocab table ##########################################################


def create_vocab_table(database: DbPath, drop: bool = False) -> None:
    """Create a table with vocabulary words and their frequencies."""
    sql = """
        create table if not exists vocab (
            word  text,
            freq  integer
        );
        """
    create_table(database, sql, drop=drop)


def insert_vocabulary_words(database: DbPath, batch: list) -> None:
    """Insert a batch of sheets records."""
    sql = """insert into vocab (word, freq) values (:word, :freq);"""
    insert_batch(database, sql, batch)


def select_vocab(database: DbPath, min_freq=2, min_len=3) -> list[dict]:
    """Get herbarium sheet image data."""
    sql = """select * from vocab where freq >= ? and length(word) >= ?"""
    return rows_as_dicts(database, sql, [min_freq, min_len])


# ############## Misspellings table ###################################################


def create_misspellings_table(database: DbPath, drop: bool = False) -> None:
    """Create a table with vocabulary words and their frequencies."""
    sql = """
        create table if not exists misspellings (
            miss  text,
            word  text,
            dist  integer,
            freq  integer
        );
        """
    create_table(database, sql, drop=drop)


def insert_misspellings(database: DbPath, batch: list) -> None:
    """Insert a batch of sheets records."""
    sql = """insert into misspellings (miss, word, dist, freq) values (?, ?, ?, ?);"""
    insert_batch(database, sql, batch)


def select_misspellings(database: DbPath, min_freq=5, min_len=3) -> list[dict]:
    """Get herbarium sheet image data."""
    sql = """select * from misspellings where freq >= ? and length(miss) >= ?"""
    return rows_as_dicts(database, sql, [min_freq, min_len])


# ############ Sheets tables ##########################################################


def create_sheets_table(database: DbPath, drop: bool = False) -> None:
    """Create a table with paths to the valid herbarium sheet images."""
    sql = """
        create table if not exists sheets (
            sheet_id integer primary key autoincrement,
            path     text    unique,
            width    integer,
            height   integer,
            coreid   text,
            split    text
        );
        create unique index if not exists sheets_idx on sheets (coreid);
        """
    create_table(database, sql, drop=drop)


def insert_sheets(database: DbPath, batch: list) -> None:
    """Insert a batch of sheets records."""
    sql = "insert into sheets (path, width, height) values (:path, :width, :height);"
    insert_batch(database, sql, batch)


def create_sheet_errors_table(database: DbPath, drop: bool = False) -> None:
    """Create a table with paths to the invalid herbarium sheet images."""
    sql = """
        create table if not exists sheet_errors (
            error_id integer primary key autoincrement,
            path     text    unique
        );
        """
    create_table(database, sql, drop=drop)


def insert_sheet_errors(database: DbPath, batch: list) -> None:
    """Insert a batch of sheets error records."""
    sql = """insert into sheet_errors (path) values (:path);"""
    insert_batch(database, sql, batch)


def select_sheets(database: DbPath, *, limit: int = 0) -> list[dict]:
    """Get herbarium sheet image data."""
    sql = """select * from sheets"""
    sql, params = build_select(sql, limit=limit)
    return rows_as_dicts(database, sql, params)


# ############ label table ##########################################################


def create_label_table(database: DbPath, drop: bool = False) -> None:
    """Create a table with the label crops of the herbarium images."""
    sql = """
        create table if not exists labels (
            label_id     integer primary key autoincrement,
            sheet_id     integer,
            label_set    text,
            offset       integer,
            class        text,
            label_left   integer,
            label_top    integer,
            label_right  integer,
            label_bottom integer
        );

        create unique index labels_idx on labels (label_set, sheet_id, offset);
        create index if not exists labels_sheet_id on labels(sheet_id);
        """
    create_table(database, sql, drop=drop)


def insert_labels(database: DbPath, batch: list) -> None:
    """Insert a batch of label records."""
    sql = """
        insert into labels
               ( sheet_id,    label_set,  offset,       class,
                 label_left,  label_top,  label_right,  label_bottom)
        values (:sheet_id,   :label_set, :offset,      :class,
                :label_left, :label_top, :label_right, :label_bottom);
    """
    insert_batch(database, sql, batch)


def select_labels(
    database: DbPath,
    *,
    limit: int = 0,
    label_sets: Optional[str] = None,
    classes: Optional[str] = None,
) -> list[dict]:
    """Get label records."""
    sql = """select * from labels join sheets using (sheet_id)"""
    sql, params = build_select(sql, class_=classes, label_set=label_sets, limit=limit)
    return rows_as_dicts(database, sql, params)


def select_label_split(
    database: DbPath, *, split: str, label_set: str, limit: int = 0
) -> list[dict]:
    """Get label records for training, validation, or testing."""
    sql = """
        select *
        from sheets
   left join labels using (sheet_id)
    """
    sql, params = build_select(sql, split=split, label_set=label_set, limit=limit)
    return rows_as_dicts(database, sql, params)


# ######### Subjects to sheets #######################################################


def create_subjects_to_sheets_table(database: DbPath, drop: bool = False) -> None:
    """Create a table to link subjects to herbarium sheets."""
    sql = """
        create table if not exists subs_to_sheets (
            subject_id integer primary key,
            path       text,
            coreid     text
        );
        create index if not exists subs_to_sheets_idx on subs_to_sheets (coreid);
    """
    create_table(database, sql, drop=drop)


# ############ ocr table #############################################################


def create_ocr_table(database: DbPath, drop: bool = False) -> None:
    """Create a table with the label crops of the herbarium images."""
    sql = """
        create table if not exists ocr (
            ocr_id     integer primary key autoincrement,
            label_id   integer,
            ocr_set    text,
            engine     text,
            pipeline   text,
            conf       real,
            ocr_left   integer,
            ocr_top    integer,
            ocr_right  integer,
            ocr_bottom integer,
            ocr_text   text
        );

        create index if not exists ocr_label_id on ocr(label_id);
        """
    create_table(database, sql, drop=drop)


def insert_ocr(database: DbPath, batch: list) -> None:
    """Insert a batch of ocr records."""
    sql = """
        insert into ocr
               ( label_id,  ocr_set,  engine,  pipeline,
                 conf,  ocr_left,  ocr_top,   ocr_right,   ocr_bottom,  ocr_text)
        values (:label_id, :ocr_set, :engine, :pipeline,
                :conf, :ocr_left, :ocr_top,  :ocr_right,  :ocr_bottom, :ocr_text);
    """
    insert_batch(database, sql, batch)


def select_ocr(
    database: DbPath, ocr_sets=None, classes=None, limit: int = 0
) -> list[dict]:
    """Get ocr box records."""
    sql = """
        select *
          from ocr
          join labels using (label_id)
          join sheets using (sheet_id)
    """
    sql, params = build_select(sql, limit=limit, class_=classes, ocr_set=ocr_sets)
    return rows_as_dicts(database, sql, params)


def get_ocr_sets(database: DbPath) -> list[dict]:
    """Get all of the OCR runs in the database."""
    sql = """select distinct ocr_set from ocr"""
    sql, params = build_select(sql)
    return rows_as_dicts(database, sql, params)


# ############ consensus table #######################################################


def create_consensus_table(database: DbPath, drop: bool = False) -> None:
    """Create a table with the reconstructed label text."""
    sql = """
        create table if not exists consensus (
            cons_id   integer primary key autoincrement,
            label_id  integer,
            cons_set  text,
            ocr_set   text,
            cons_text text
        );
        create index if not exists cons_label_id on consensus (label_id);
        """
    create_table(database, sql, drop=drop)


def insert_consensus(database: DbPath, batch: list) -> None:
    """Insert a batch of consensus records."""
    sql = """
        insert into consensus
               ( label_id,  cons_set,  ocr_set,  cons_text)
        values (:label_id, :cons_set, :ocr_set, :cons_text);
    """
    insert_batch(database, sql, batch)


def select_consensus(
    database: DbPath,
    cons_set: str = "",
    limit: int = 0,
) -> list[dict]:
    """Get consensus records."""
    sql = """
        select *
          from consensus
          join labels using (label_id)
          join sheets using (sheet_id)
    """
    sql, params = build_select(sql, limit=limit, cons_set=cons_set)
    return rows_as_dicts(database, sql, params)
