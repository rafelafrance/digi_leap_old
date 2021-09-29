"""Utilities for digi_leap.sqlite databases."""

import sqlite3


def select_records(database, sql, limit=0):
    """Get ocr_results records."""
    sql += f" limit {limit}" if limit else ""

    with sqlite3.connect(database) as cxn:
        cxn.row_factory = sqlite3.Row
        return cxn.execute(sql)


def insert_batch(database, sql, batch):
    """Insert a batch of sheets records."""
    if batch:
        with sqlite3.connect(database) as cxn:
            cxn.executemany(sql, batch)


# ############ Sheets tables ##########################################################


def create_sheets_table(database, drop=False):
    """Create a table with paths to the valid herbarium sheet images."""
    with sqlite3.connect(database) as cxn:
        if drop:
            cxn.executescript("""drop table if exists sheets;""")

        cxn.executescript(
            """
            create table if not exists sheets (
                path   text primary key,
                width  integer,
                height integer
            );
            """
        )


def insert_sheets(database, batch):
    """Insert a batch of sheets records."""
    sql = """
        insert into sheets (path, width, height) values (:path, :width, :height);
    """
    insert_batch(database, sql, batch)


def create_sheet_errors_table(database, drop=False):
    """Create a table with paths to the invalid herbarium sheet images."""
    with sqlite3.connect(database) as cxn:
        if drop:
            cxn.executescript("""drop table if exists sheet_errors;""")

        cxn.executescript(
            """
            create table if not exists sheet_errors (
                path text unique
            );
            """
        )


def insert_sheet_errors(database, batch):
    """Insert a batch of sheets error records."""
    sql = """insert into sheet_errors (path) values (:path);"""
    insert_batch(database, sql, batch)


def select_sheets(database, limit=0):
    """Get herbarium sheet image data."""
    sql = """select path, width, height from sheets"""
    return select_records(database, sql, limit)


def select_sheet_paths(database, limit=0):
    """Get herbarium sheet image paths."""
    return [p["path"] for p in select_sheets(database, limit)]


# ############ label table ##########################################################


def create_label_table(database, drop=False):
    """Create a table with the label crops of the herbarium images."""
    with sqlite3.connect(database) as cxn:
        if drop:
            cxn.executescript("""drop table if exists labels;""")

        cxn.executescript(
            """
            create table if not exists labels (
                path   text,
                offset integer,
                class  text,
                left   integer,
                top    integer,
                right  integer,
                bottom integer,
                primary key (path, offset)
            );
            """
        )


def insert_labels(database, batch):
    """Insert a batch of label records."""
    sql = """
        insert into labels
               ( path,  offset,  class,  left,  top,  right,  bottom)
        values (:path, :offset, :class, :left, :top, :right, :bottom);
    """
    insert_batch(database, sql, batch)


def select_labels(database, limit=0):
    """Get label records."""
    sql = """select path, offset, class, left, top, right, bottom from labels"""
    return select_records(database, sql, limit)


# ############ ocr_results table ######################################################


def create_ocr_results_table(database, drop=False):
    """Create a table with the label crops of the herbarium images."""
    with sqlite3.connect(database) as cxn:
        if drop:
            cxn.executescript("""drop table if exists ocr_results;""")

        cxn.executescript(
            """
            create table if not exists ocr_results (
                path     text,
                offset   integer,
                engine   text,
                pipeline text,
                conf     real,
                left     integer,
                top      integer,
                right    integer,
                bottom   integer,
                text     text,
                primary key (path, offset, engine, pipeline)
            );
            """
        )


def insert_ocr_results(database, batch):
    """Insert a batch of label records."""
    sql = """
        insert into ocr_results
               ( path,  offset,  engine,  pipeline,  conf,
                 left,  top,  right,  bottom,  text)
        values (:path, :offset, :engine, :pipeline, :conf,
                :left, :top, :right, :bottom, :text);
    """
    insert_batch(database, sql, batch)


def select_ocr_results(database, limit=0):
    """Get ocr_results records."""
    sql = """
        select path, offset, engine, pipeline, conf, left, top, right, bottom, text
          from ocr_results
    """
    return select_records(database, sql, limit)
