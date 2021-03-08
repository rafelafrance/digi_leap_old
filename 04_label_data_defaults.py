#!/usr/bin/env python
"""
Get data we can use to fill in missing fields."""

import re
import sqlite3
from random import seed

from digi_leap.pylib.const import AUG_FILES, LABEL_DB


def sex_defaults(path):
    """Setup default sexes."""
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


def name_defaults(label_db, path):
    """Setup reasonable defaults for names by using existing names."""
    sql = """
        SELECT DISTINCT scientific_name_authorship FROM data
        UNION SELECT DISTINCT name_according_to FROM data
        UNION SELECT DISTINCT georeferenced_by FROM data
        UNION SELECT DISTINCT record_entered_by FROM data
        UNION SELECT DISTINCT recorded_by FROM data
    """
    with sqlite3.connect(label_db) as cxn:
        cursor = cxn.execute(sql)
        lines = {f'{n}\n' for r in cursor.fetchall()
                 if (n := re.sub(r'\s*\([:/()\d\s-]+$', '', r[0])) and len(n) > 2}
        lines = sorted(lines)

    with open(path, 'w') as out_file:
        out_file.writelines(lines)


def date_defaults(label_db, path):
    """Get dates we can use for generating labels."""
    sql = """
        select distinct date_identified from data
        union select distinct event_date from data
        union select distinct dwc_verbatim_event_data from data
    """
    with sqlite3.connect(label_db) as cxn:
        cursor = cxn.execute(sql)
        lines = [f'{n}\n' for r in cursor.fetchall() if (n := r[0])]

    with open(path, 'w') as out_file:
        out_file.writelines(lines)


if __name__ == '__main__':
    seed(123)
    sex_defaults(AUG_FILES['sex'])
    date_defaults(LABEL_DB, AUG_FILES['date'])
    name_defaults(LABEL_DB, AUG_FILES['name'])
