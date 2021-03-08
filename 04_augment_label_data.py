#!/usr/bin/env python
"""
Augment the label data.

This module augments the raw data for the labels. So far this is mostly
filling null fields with data and not actually changing text.
"""

import sqlite3

import pandas as pd

from digi_leap.pylib.const import LABEL_DB


def get_label_data(label_db):
    """Get the data from the newly created label_data table."""
    with sqlite3.connect(label_db) as cxn:
        df = pd.read_sql('select * from data', cxn)
    return df


def augment_sex(df):
    """Augment the sex field."""
    sexes = {
        'Male': 10_000,
        'male': 10_000,
        'Female': 10_000,
        'female': 10_000,
        'hermaphrodite': 10,
        'bisexual': 10,
        '♀': 5_000,
        '♂': 5_000,
        '⚥': 10,
    }

    for value, count in sexes.items():
        rows = df.sample(n=count)
        df.loc[rows.index, 'sex'] = value

    return df


def insert_data(df, label_db):
    """Write the data to the smaller database."""
    with sqlite3.connect(label_db) as cxn:
        df.to_sql('data', cxn, if_exists='replace', index=False)


def augment_data(label_db):
    """Create the label data table with augmented text data."""
    df = get_label_data(label_db)

    df = augment_sex(df)

    insert_data(df, label_db)


if __name__ == '__main__':
    augment_data(LABEL_DB)
