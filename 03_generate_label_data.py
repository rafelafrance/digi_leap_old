#!/usr/bin/env python
"""
Generate Label Text by Sampling iDigBio Data

This will create persistent data for the label that will be used for
generating the labels. The entire table (or CSV) file containing the
raw text is too large and cumbersome to work with, so we're going to
trim it down to a manageable and easily sharable size.
"""

import sqlite3

import pandas as pd

from digi_leap.pylib.const import LABEL_DB, RAW_DATA, RAW_DB
from digi_leap.pylib.util import ended, read_lines, started

RAW_DATA_COUNT = 1_000_000  # A pool of data to sample fields

COLUMNS = read_lines('columns')  # Columns to take from the raw data


def create_data_table(raw_db, raw_data, raw_data_count, label_db, columns):
    """Sample the rows from the raw data and get the columns."""
    columns = {f'`{c}`' for c in columns}
    columns = ', '.join(columns)

    sql = f"""
        CREATE TABLE IF NOT EXISTS aux.data AS
            SELECT rowid AS data_id, {columns}
              FROM {raw_data}
             WHERE rowid IN (
                 SELECT rowid
                   FROM {raw_data}
                  WHERE kingdom like 'plant%'
                    AND scientific_name <> ''
               ORDER BY RANDOM()
                  LIMIT {raw_data_count})
    """

    with sqlite3.connect(raw_db) as cxn:
        cxn.execute(f"ATTACH DATABASE '{label_db}' AS aux")
        cxn.execute('DROP TABLE IF EXISTS aux.data')
        cxn.execute(sql)

    with sqlite3.connect(label_db) as cxn:
        cxn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
                data_data_id ON data (data_id)""")


def get_label_data(label_db):
    """Get the data from the newly created label_data table."""
    with sqlite3.connect(label_db) as cxn:
        df = pd.read_sql('select * from data', cxn)
    df = df.reindex(columns=['data_id'] + COLUMNS)  # An easier order to navigate
    return df


def insert_data(df, label_db):
    """Write the data to the smaller database."""
    with sqlite3.connect(label_db) as cxn:
        df.to_sql('data', cxn, if_exists='replace', index=False)


def build_label_data(raw_db, raw_data, raw_data_count, label_db, columns):
    """Create the label data table with augmented text data."""
    create_data_table(raw_db, raw_data, raw_data_count, label_db, columns)
    df = get_label_data(label_db)
    insert_data(df, label_db)


if __name__ == '__main__':
    started()

    build_label_data(RAW_DB, RAW_DATA, RAW_DATA_COUNT, LABEL_DB, COLUMNS)

    ended()
