"""Utilities for digi_leap.sqlite databases."""


def create_sheets_table(cxn, clear=False):
    """Create a table with paths to the valid herbarium sheet images."""
    if clear:
        cxn.executescript("""drop table if exists sheets;""")

    cxn.executescript("""
        create table if not exists sheets (
            path text unique
        );
        """)


def insert_sheets_batch(cxn, batch):
    """Insert a batch of sheets records."""
    sql = """insert into sheets (path) values (?);"""
    with cxn:
        cxn.executemany(sql, batch)


def create_sheet_errors_table(cxn, clear=False):
    """Create a table with paths to the invalid herbarium sheet images."""
    if clear:
        cxn.executescript("""drop table if exists sheet_errors;""")

    cxn.executescript("""
        create table if not exists sheet_errors (
            path text unique
        );
        """)


def insert_sheet_errors_batch(cxn, batch):
    """Insert a batch of sheets error records."""
    sql = """insert into sheet_errors (path) values (?);"""
    with cxn:
        cxn.executemany(sql, batch)
