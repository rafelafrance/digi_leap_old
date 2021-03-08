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

from digi_leap.pylib.const import LABEL_DB, RAW_DATA, RAW_DATA_COUNT, RAW_DB

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
    build_label_data(RAW_DB, RAW_DATA, RAW_DATA_COUNT, LABEL_DB, COLUMNS)
