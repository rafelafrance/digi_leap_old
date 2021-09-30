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


def create_table(database, sql, table, drop=False):
    """Create a table with paths to the valid herbarium sheet images."""
    with sqlite3.connect(database) as cxn:
        if drop:
            cxn.executescript(f"""drop table if exists {table};""")

        cxn.executescript(sql)


# ############ Sheets tables ##########################################################


def create_sheets_table(database, drop=False):
    """Create a table with paths to the valid herbarium sheet images."""
    sql = """
        create table if not exists sheets (
            sheet_id integer primary key autoincrement,
            path     text    unique,
            width    integer,
            height   integer
        );
        """
    create_table(database, sql, "sheets", drop=drop)


def insert_sheets(database, batch):
    """Insert a batch of sheets records."""
    sql = """
        insert into sheets (path, width, height) values (:path, :width, :height);
    """
    insert_batch(database, sql, batch)


def create_sheet_errors_table(database, drop=False):
    """Create a table with paths to the invalid herbarium sheet images."""
    sql = """
        create table if not exists sheet_errors (
            error_id integer primary key autoincrement,
            path     text    unique
        );
        """
    create_table(database, sql, "sheet_errors", drop=drop)


def insert_sheet_errors(database, batch):
    """Insert a batch of sheets error records."""
    sql = """insert into sheet_errors (path) values (:path);"""
    insert_batch(database, sql, batch)


def select_sheets(database, limit=0):
    """Get herbarium sheet image data."""
    sql = """select sheet_id, path, width, height from sheets"""
    return select_records(database, sql, limit)


def select_sheet_paths(database, limit=0):
    """Get herbarium sheet image paths."""
    return [p["path"] for p in select_sheets(database, limit)]


# ############ label table ##########################################################


def create_label_table(database, drop=False):
    """Create a table with the label crops of the herbarium images."""
    sql = """
        create table if not exists labels (
            label_id integer primary key autoincrement,
            path     text,
            offset   integer,
            class    text,
            left     integer,
            top      integer,
            right    integer,
            bottom   integer
        );
        """
    create_table(database, sql, "labels", drop=drop)


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
    sql = """
        select label_id, path, offset, class, left, top, right, bottom from labels
    """
    return select_records(database, sql, limit)


# ############ ocr_results table ######################################################


def create_ocr_results_table(database, drop=False):
    """Create a table with the label crops of the herbarium images."""
    sql = """
        create table if not exists ocr_results (
            ocr_id   integer primary key autoincrement,
            run      text,
            path     text,
            offset   integer,
            engine   text,
            pipeline text,
            conf     real,
            left     integer,
            top      integer,
            right    integer,
            bottom   integer,
            text     text
        );
        """
    create_table(database, sql, "ocr_results", drop=drop)


def insert_ocr_results(database, batch):
    """Insert a batch of label records."""
    sql = """
        insert into ocr_results
               ( run,   path,  offset,  engine,  pipeline,  conf,
                 left,  top,   right,   bottom,  text)
        values (:run,  :path, :offset, :engine, :pipeline, :conf,
                :left, :top,  :right,  :bottom, :text);
    """
    insert_batch(database, sql, batch)


def select_ocr_results(database, limit=0):
    """Get ocr_results records."""
    sql = """
        select ocr_id, run, path,  offset, engine, pipeline, conf,
               left,   top, right, bottom, text
          from ocr_results
    """
    return select_records(database, sql, limit)
