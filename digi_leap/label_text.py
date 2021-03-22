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

from digi_leap.const import DATA_DIR
from digi_leap.label_fragment import LabelFragment, Use, Writing

REMOVE_PUNCT = str.maketrans('', '', string.punctuation)

with open(DATA_DIR / 'disallowed_values.txt') as in_file:
    DISALLOWED = [v.strip() for v in in_file.readlines() if v] + ['']
DISALLOWED_VALUES = [f"'{v}'" for v in DISALLOWED]
DISALLOWED_VALUES = ', '.join(DISALLOWED_VALUES)


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
                records.append(LabelFragment(
                    label_id=self.label_id,
                    writing=col.get('writing', Writing.typewritten).name,
                    row=r,
                    col=c,
                    text=col['text'],
                    use=col['use'].name,
                ))
        return records

    def add_row(self, *cols):
        """Add a row to the label."""
        cols = [c for c in cols if c['text']]
        if cols:
            self.label.append(cols)

    @staticmethod
    def col(text='', use=Use.text, line=0, writing=Writing.typewritten):
        """Add a segment/column of text to the label row."""
        return {'text': text, 'use': use, 'line': line, 'writing': writing}

    @staticmethod
    def is_valid_value(value):
        """Check if the given value is empty or is disallowed."""
        return value and value.lower().translate(REMOVE_PUNCT) not in DISALLOWED

    def update_by_use(self, use, field, value):
        """Set all record fields with the given use to the value."""
        for row in self.label:
            for col in row:
                if col['use'] == use:
                    col[field] = value

    def text(self, text, use=Use.text, writing=Writing.typewritten):
        """Add text as is to the label."""
        self.add_row(self.col(text, use, writing=writing))

    def impute_text(
            self,
            text,
            defaults,
            use=Use.text,
            field_label='',
            writing=Writing.typewritten):
        """Get a value using a set of defaults if it is not found."""
        text = text if text else choice(defaults)
        self.long_text(text, use=use, field_label=field_label, writing=writing)

    def long_text(
            self, text='', use=Use.text, field_label='', writing=Writing.typewritten):
        """Split long text into multiple rows of text."""
        line = 0

        if field_label:
            split = self.max_row_len - len(field_label)
            first, text = text[:split], text[split:].lstrip()
            if self.is_valid_value(first):
                self.add_row(
                    self.col(text, Use.field_label),
                    self.col(first, use, writing=writing))
                line = 1

        for frag in wrap(text):
            if self.is_valid_value(frag):
                col = self.col(frag, use, line, writing=writing)
                self.add_row(col)
                line += 1

    def layout_by_field(self, *text, uses=None, writing=Writing.typewritten):
        """Layout text so that long lines are split on the field."""
        uses = uses if uses else Use.text
        uses = uses if isinstance(uses, list) else [uses]

        cols = [self.col(t, u) for t, u in zip_longest(text, uses, fillvalue=uses[-1])
                if t]

        # Check length of text + the spaces between the text with the max row length
        if sum((len(t) + 1) for t in text) < self.max_row_len:
            self.add_row(*cols)
        else:
            line = 0
            prev_use = ''
            for col in cols:
                if prev_use != col['use']:
                    line = 0

                col['line'] = line
                col['writing'] = writing

                self.add_row(col)

                prev_use = col['use']
                line += 1

    # ########################################################################
    # Generate text for specific types of data

    def sci_name(self):
        """Add a scientific name row."""
        name = self.record['dwc:scientificName']
        auth = self.record['dwc:scientificNameAuthorship']
        if name.find(auth) > -1:
            auth = ''
        self.layout_by_field(name, auth, uses=[Use.sci_name, Use.auth])

    def lat_long(self):
        """Add a latitude and longitude to the label."""
        lat = self._dms(self.record['dwc:verbatimLatitude'])
        long = self._dms(self.record['dwc:verbatimLongitude'])
        self.layout_by_field(lat, long, uses=Use.lat_long)

    @staticmethod
    def _dms(lat_lng):
        """Add degree, minute, second symbols."""
        frags = lat_lng.split()
        if re.match(r'\d+ \d+ \d+(?:\.\d+)? [NnSsEeWw]]', lat_lng):
            deg, min_, sec, dir_ = frags
            lat_lng = f'[~]?{deg}°{min_}′{sec}″{dir_}'
        elif re.match(r'\d+ \d+ [NnSsEeWw]]', lat_lng):
            deg, min_, dir_ = frags
            lat_lng = f'[~]?{deg}°{min_}′{dir_}'
        return lat_lng

    def title(self):
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
            self.add_row(self.col(title, Use.title))
