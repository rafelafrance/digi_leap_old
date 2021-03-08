#!/usr/bin/env python
"""
Generate label text from the saved label data.

Images can be generated (both clean and dirty) on the fly but we need to
persist the text data so that it can be used in several steps further down
the pipeline. This module creates persistent data for the label text from the
iDigBio database.

Each row in the label text can be used to generate several types of labels as
well as modifying the text itself. The text will be saved in parts so that
image augmentation can be done on each section of text separately. Note that
we are generating plausible looking labels not necessarily realistic labels.

Some text augmentation:
- Sometimes we will use field labels and other times not
- Add titles and headers
- Fields can be moved around on the label
- Omit and add data to the labels
- Augment taxon names with data from ITIS
- Generate names dates and numbers
- Replace some words with abbreviations
- Add extra spaces
- Join fields to make longer text fields

** Image augmentation happens elsewhere.

Some fields we needed:
- The label type
- The text itself
- If the field is typed or cursive or a barcode
- Row/vertical order
- Column/horizontal order
"""

import sqlite3

import pandas as pd

from digi_leap.pylib.const import LABEL_DB


def get_label_data(label_db):
    """Get the data from the newly created label_data table."""
    with sqlite3.connect(label_db) as cxn:
        df = pd.read_sql('select * from data', cxn)
    return df


def insert_data(df, label_db):
    """Write the data to the smaller database."""
    with sqlite3.connect(label_db) as cxn:
        df.to_sql('data', cxn, if_exists='replace', index=False)


def augment_data(label_db):
    """Create the label data table with augmented text data."""
    df = get_label_data(label_db)

    insert_data(df, label_db)


if __name__ == '__main__':
    augment_data(LABEL_DB)
