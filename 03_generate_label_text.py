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

from digi_leap.pylib.const import LABEL_DB, RAW_DATA_COUNT, RAW_DB, RAW_DATA

# These column look good for label generation
COLUMNS = """
    scientific_name
    phylum
    class
    order
    family
    genus
    subgenus
    verbatim_scientific_name
    accepted_name_usage
    vernacular_name
    taxon_rank
    verbatim_taxon_rank

    scientific_name_authorship
    name_according_to
    name_published_in
    name_published_in_id
    name_published_in_year
    date_identified
    identified_by
    identification_id
    identification_remarks
    original_name_usage
    previous_identifications

    locality
    location_remarks
    country
    state_province
    municipality
    water_body
    georeference_remarks
    georeferenced_by

    verbatim_coordinate_system
    verbatim_coordinates
    verbatim_depth
    verbatim_elevation
    verbatim_latitude
    verbatim_longitude
    verbatim_srs

    event_date
    event_id
    event_remarks
    dwc_verbatim_event_date

    owner_institution_code
    catalog_number
    collection_code
    dataset_name

    field_notes
    field_number

    habitat
    life_stage
    occurrence_remarks
    organism_remarks
    preparations
    reproductive_condition
    sex
    sampling_protocol
    type_status
    
    record_entered_by
    record_number
    recorded_by
""".split()


def create_data_table(raw_db, raw_data, raw_data_count, label_db, columns):
    """Sample the rows from the raw data and get the columns."""
    columns = {f'`{c}`' for c in columns}
    columns = ', '.join(columns)

    sql = f"""
        CREATE TABLE IF NOT EXISTS aux.data AS
            SELECT rowid AS id, {columns}
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
        cxn.execute(sql)

    # We will need this index
    with sqlite3.connect(label_db) as cxn:
        cxn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
                data_id ON data (id)""")


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


def build_label_data(raw_db, raw_data, raw_data_count, label_db, columns):
    """Create the label data table with augmented text data."""
    create_data_table(raw_db, raw_data, raw_data_count, label_db, columns)
    df = get_label_data(label_db)

    df = augment_sex(df)

    insert_data(df, label_db)


if __name__ == '__main__':
    build_label_data(RAW_DB, RAW_DATA, RAW_DATA_COUNT, LABEL_DB, COLUMNS)
