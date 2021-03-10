#!/usr/bin/env python
"""Get data we can use for imputation."""

import argparse
import sqlite3
import textwrap

import pandas as pd

from digi_leap.pylib.const import REJECT_VALUES
from digi_leap.pylib.util import ended, log, started


def sex_values(args):
    """Setup default sexes."""
    log('Getting sex values')

    recs = [
        {'sex': 'Female', 'count': 100},
        {'sex': 'female', 'count': 100},
        {'sex': 'Male', 'count': 100},
        {'sex': 'male', 'count': 100},
        {'sex': 'bisexual', 'count': 1},
        {'sex': 'hermaphrodite', 'count': 1},
        {'sex': '♀', 'count': 50},
        {'sex': '♂', 'count': 50},
        {'sex': '⚥', 'count': 1},
        {'sex': '', 'count': 1000}
    ]
    df = pd.DataFrame(recs)
    with sqlite3.connect(args.database) as cxn:
        df.to_sql('sex', cxn, if_exists='replace', index=False)


def name_values(args):
    """Setup reasonable defaults for names by using existing names."""
    log('Getting name values')

    sql = f"""
        create table if not exists names as
        with agg as (
            select distinct `dwc:recordedBy` as name from {args.input_table}
            union select distinct `dwc:nameAccordingTo` from {args.input_table}
            union select distinct `dwc:georeferencedBy` from {args.input_table}
            union select distinct `symbiota:recordEnteredBy` from {args.input_table}
        )
        select name from agg
        where lower(name) not in ({REJECT_VALUES})
        order by random()
        limit {args.limit}
    """

    with sqlite3.connect(args.database) as cxn:
        cxn.execute(sql)


def date_values(args):
    """Get dates we can use for generating labels."""
    log('Getting date values')

    sql = f"""
        create table if not exists dates as
        with agg as (
            select distinct `dwc:eventDate` as `date` from {args.input_table}
            union select distinct `dwc:dateIdentified` from {args.input_table}
            union select distinct `dwc:VerbatimEventDate` from {args.input_table}
            union select distinct `dwc:verbatimEventDate_1` from {args.input_table}
        )
        select `date` from agg
        where lower(`date`) not in ({REJECT_VALUES})
        order by random()
        limit {args.limit}
     """

    with sqlite3.connect(args.database) as cxn:
        cxn.execute(sql)


def right_holder_values(args):
    """Get rights holders we can use for generating labels."""
    log('Getting rights_holder values')

    sql = f"""
        create table rights_holders as
        with agg as (
            select distinct `dcterms:rightsHolder` as rights_holder 
              from {args.input_table}
        )
        select rights_holder from agg
        where lower(rights_holder) not in ({REJECT_VALUES})
        order by random()
        limit {args.limit}
    """

    with sqlite3.connect(args.database) as cxn:
        cxn.execute(sql)


def parse_args():
    """Process command-line arguments."""
    description = """Get data we can use for imputation."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--database', '-d', required=True,
        help="""Path to the output database. This is a temporary database that
            will later be sampled and then deleted.""")

    arg_parser.add_argument(
        '--input-table', '-i', required=True,
        help=f"""Draw the data from various (currently hard-coded) fields in 
            this table.""")

    default = 1_000_000
    arg_parser.add_argument(
        '--limit', '-l', type=int, default=default,
        help=f"""Limit the number of values in the generated tables to this.
            The default is {default}.""")

    args = arg_parser.parse_args()

    return args


def imputable_values(args):
    """Create the values used for imputation."""
    sex_values(args)
    right_holder_values(args)
    date_values(args)
    name_values(args)


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    imputable_values(ARGS)

    ended()
