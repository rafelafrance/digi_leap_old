"""Label object.

Label text is a list of rows with each row being a list of 'columns' and each
column is a dict of data that will go into the database record. So, it's a
ragged 2-dimensional array of dicts.
"""

import re
import string
import uuid
from itertools import zip_longest
from random import choice, random
from textwrap import wrap

from digi_leap.pylib.const import DISALLOWED
from digi_leap.pylib.util import DotDict

REMOVE_PUNCT = str.maketrans('', '', string.punctuation)


class LabelText:
    """Build label text from DB data."""

    def __init__(self, record, max_row_len=40):
        self.label_id = str(uuid.uuid4())
        self.record = record
        self.max_row_len = max_row_len
        self.label = []

    def build_records(self):
        """Fill in the rest of the label data."""
        records = []
        for r, row in enumerate(self.label):
            for c, col in enumerate(row):
                records.append({
                    'label_id': self.label_id,
                    'font': 'typewritten',
                    'row': r,
                    'col': c,
                    'text': col.text,
                    'use': col.use,
                })
        return records

    def add_row(self, *cols):
        """Add a row to the label."""
        cols = [c for c in cols if c.text]
        if cols:
            self.label.append(cols)

    @staticmethod
    def col(text='', use='text'):
        """Add a segment/column of text to the label row."""
        return DotDict({
            'text': text,
            'use': use,
        })

    @staticmethod
    def is_valid_value(value):
        """Check if the given value is empty or is disallowed."""
        return value and value.lower().translate(REMOVE_PUNCT) not in DISALLOWED

    def impute_text(self, text, defaults, use='', field_label=''):
        """Get a value using a set of defaults if it is not found."""
        text = text if text else choice(defaults)
        self.split_text(text, use=use, field_label=field_label)

    def split_text(self, text='', use='text', field_label=''):
        """Split longer text into multiple rows of text."""
        if field_label:
            split = self.max_row_len - len(field_label)
            first, text = text[:split], text[split:].lstrip()
            if self.is_valid_value(first):
                self.add_row(
                    self.col(text, 'field_label'),
                    self.col(first, use),
                )
        for frag in wrap(text):
            if self.is_valid_value(frag):
                col = self.col(frag, use)
                self.add_row(col)

    def split_columns(self, *text, uses=None):
        """If the total text length > max row length then split the text."""
        uses = uses if uses else 'text'
        uses = uses if isinstance(uses, list) else [uses]

        cols = [self.col(t, u) for t, u in zip_longest(text, uses, fillvalue=uses[-1])]

        if sum(len(t) for t in text) < self.max_row_len - len(text) + 1:
            self.add_row(*cols)
        else:
            _ = [self.add_row(c) for c in cols]

    # ########################################################################
    # Specific row types

    def add_sci_name(self, use='sci_name', auth_use='auth'):
        """Add a scientific name row."""
        name = self.record['dwc:scientificName']
        auth = self.record['dwc:scientificNameAuthorship']
        if name.find(auth) > -1:
            auth = ''
        self.split_columns(name, auth, uses=[use, auth_use])

    def add_lat_long(self):
        """Add a latitude and longitude to the label."""
        lat = self._add_dms(self.record['dwc:verbatimLatitude'])
        long = self._add_dms(self.record['dwc:verbatimLongitude'])
        self.split_columns(lat, long, 'lat_long')

    @staticmethod
    def _add_dms(lat_long):
        """Add degree, minute, second symbols"""
        frags = lat_long.split()
        if re.match(r'\d+ \d+ \d+(?:\.\d+)? [NnSsEeWw]]', lat_long):
            deg, min_, sec, dir_ = frags
            lat_long = f'[~]?{deg}°{min_}′{sec}″{dir_}'
        elif re.match(r'\d+ \d+ [NnSsEeWw]]', lat_long):
            deg, min_, dir_ = frags
            lat_long = f'[~]?{deg}°{min_}′{dir_}'
        return lat_long

    def add_title(self):
        """Add title to the label."""
        title = ''
        if self.record['dwc:stateProvince']:
            if random() < 0.5:
                title = 'Plants of ' + self.record['dwc:stateProvince']
            else:
                title = self.record['dwc:stateProvince'] + ' Plants'
        elif self.record['dwc:datasetName']:
            if random() < 0.5:
                title = 'Collection of ' + self.record['dwc:datasetName']
            else:
                title = self.record['dwc:datasetName'] + ' Collection'

        if title:
            self.add_row(self.col(title, 'title'))
