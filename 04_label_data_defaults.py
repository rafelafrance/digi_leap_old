#!/usr/bin/env python
"""
Get data we can use to fill in missing fields."""

import re
import sqlite3

from digi_leap.pylib.const import DEFAULT_FILES, LIMIT, RAW_DB  # , LABEL_DB
from digi_leap.pylib.util import ended, log, started


def sex_defaults(path):
    """Setup default sexes."""
    log('Getting sex defaults')

    lines = [
        'sex,count\n',
        f'Female,10000\n',
        f'female,10000\n',
        f'Male,10000\n',
        f'male,10000\n',
        f'hermaphrodite,100\n',
        f'bisexual,100\n',
        f'♀,5000\n',
        f'♂,5000\n',
        f'⚥,100\n',
    ]
    with open(path, 'w') as out_file:
        out_file.writelines(lines)


def name_defaults(db, table, path):
    """Setup reasonable defaults for names by using existing names."""
    log('Getting name defaults')

    sql = f"""
        with names as (
            select distinct scientific_name_authorship as nm from {table}
            union select distinct name_according_to from {table}
            union select distinct georeferenced_by from {table}
            union select distinct record_entered_by from {table}
            union select distinct recorded_by from {table}
        )
        select nm from names
        order by random()
        limit {LIMIT}
    """
    with sqlite3.connect(db) as cxn:
        cursor = cxn.execute(sql)
        lines = {f'{n}\n' for r in cursor.fetchall()
                 if (n := re.sub(r'\s*\([:/()\d\s-]+$', '', r[0])) and len(n) > 2}
        lines = sorted(lines)

    with open(path, 'w') as out_file:
        out_file.writelines(lines)


def date_defaults(db, table, path):
    """Get dates we can use for generating labels."""
    log('Getting date defaults')

    sql = f"""
        with dates as (
            select distinct date_identified as dt from {table}
            union select distinct event_date from {table}
            union select distinct verbatim_event_date from {table}
            union select distinct dwc_verbatim_event_date from {table}
        )
        select dt from dates
        order by random()
        limit {LIMIT}
    """
    with sqlite3.connect(db) as cxn:
        cursor = cxn.execute(sql)
        lines = [f'{n}\n' for r in cursor.fetchall() if (n := r[0])]
        lines = sorted(lines)

    with open(path, 'w') as out_file:
        out_file.writelines(lines)


def right_holder_defaults(db, table, path):
    """Get rights holders we can use for generating labels."""
    log('Getting rights_holder defaults')

    sql = f""" select distinct rights_holder from {table} """
    with sqlite3.connect(db) as cxn:
        cursor = cxn.execute(sql)
        lines = [f'{n}\n' for r in cursor.fetchall() if (n := r[0])]
        lines = sorted(lines)

    with open(path, 'w') as out_file:
        out_file.writelines(lines)


if __name__ == '__main__':
    started()

    TABLE = 'occurrence_raw'
    sex_defaults(DEFAULT_FILES['sex'])

    # date_defaults(LABEL_DB, 'data', DEFAULT_FILES['date'])
    # name_defaults(LABEL_DB, 'data', DEFAULT_FILES['name'])
    # right_holder_defaults(LABEL_DB, 'data', DEFAULT_FILES['rights_holder'])

    date_defaults(RAW_DB, TABLE, DEFAULT_FILES['date'])
    name_defaults(RAW_DB, TABLE, DEFAULT_FILES['name'])
    right_holder_defaults(RAW_DB, TABLE, DEFAULT_FILES['rights_holder'])

    ended()
