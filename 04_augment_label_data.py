#!/usr/bin/env python
"""
Generate Label Text by Sampling iDigBio Data

Images can be generated (both clean and dirty) on the fly but we need to
persist the text data so that it can be used in several steps further down
the pipeline. This will create persistent data for the label text from the
iDigBio database. I'm going to create a separate DB so that it can be easily
used by other team members.

The data will be in parts so that we can treat the different parts separately
when we generate the labels. For instance some parts may use different fonts and
others may have the text underlined etc. Also note that some of the parts may
be empty. We might add labels.

Some ext augmentation is done here because the OCR step, later on, needs to
replicate the text. Text augmentation steps:
- [X] Use symbols like: ♀ or ♂ and other ones that may appear on labels
- [ ] Augment taxon names with data from ITIS
- [ ] Augment location data from gazetteer data
- [ ] Generate names dates and numbers
- [ ] Replace some words with abbreviations
- [ ] Add extra spaces

Note that we are generating *"plausible looking"* labels not necessarily
*realistic* labels.

Also note that there are different kinds of labels.
- The main label that describes the sample
- Labels for species determination
- Barcode and QR-Code labels
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
