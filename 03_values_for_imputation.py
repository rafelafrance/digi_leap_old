#!/usr/bin/env python
"""Get data we can use for imputation."""

import argparse
import logging
import sqlite3
import textwrap
from random import choices, seed

import pandas as pd

from digi_leap.label_text import DISALLOWED_VALUES
from digi_leap.log import finished, started


def imputable_values(args):
    """Create the values used for imputation."""
    if args.seed:
        seed(args.seed)

    sex_values(args)
    right_holder_values(args)
    date_values(args)
    name_values(args)


def sex_values(args):
    """Setup default sexes."""
    logging.info('Getting sex values')

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
    logging.info('Getting name values')

    sql = f"""
        with agg as (
            select distinct `dwc:recordedBy` as name from {args.input_table}
            union select distinct `dwc:nameAccordingTo` from {args.input_table}
            union select distinct `dwc:georeferencedBy` from {args.input_table}
            union select distinct `symbiota:recordEnteredBy` from {args.input_table}
        )
        select name from agg
        where lower(name) not in ({DISALLOWED_VALUES})
    """

    with sqlite3.connect(args.database) as cxn:
        values = [n[0] for n in cxn.execute(sql).fetchall()]
        count = args.count if args.count <= len(values) else len(values)
        values = choices(values, count)

        df = pd.DataFrame({'name': values})
        df.to_sql('names', cxn, index=False)


def date_values(args):
    """Get dates we can use for generating labels."""
    logging.info('Getting date values')

    sql = f"""
        with agg as (
            select distinct `dwc:eventDate` as `date` from {args.input_table}
            union select distinct `dwc:dateIdentified` from {args.input_table}
            union select distinct `dwc:VerbatimEventDate` from {args.input_table}
            union select distinct `dwc:verbatimEventDate_1` from {args.input_table}
        )
        select `date` from agg
        where lower(`date`) not in ({DISALLOWED_VALUES})
     """

    with sqlite3.connect(args.database) as cxn:
        values = [n[0] for n in cxn.execute(sql).fetchall()]
        count = args.count if args.count <= len(values) else len(values)
        values = choices(values, count)

        df = pd.DataFrame({'date': values})
        df.to_sql('dates', cxn, index=False)


def right_holder_values(args):
    """Get rights holders we can use for generating labels."""
    logging.info('Getting rights_holder values')

    sql = f"""
        with agg as (
            select distinct `dcterms:rightsHolder` as rights_holder 
              from {args.input_table}
        )
        select rights_holder from agg
        where lower(rights_holder) not in ({DISALLOWED_VALUES})
    """

    with sqlite3.connect(args.database) as cxn:
        values = [n[0] for n in cxn.execute(sql).fetchall()]
        count = args.count if args.count <= len(values) else len(values)
        values = choices(values, count)

        df = pd.DataFrame({'rights_holder': values})
        df.to_sql('rights_holders', cxn, index=False)


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

    arg_parser.add_argument(
        '--count', '-C', type=int, default=1_000_000,
        help=f"""Limit the number of values in the generated tables to this.
            (default: %(default)s)""")

    arg_parser.add_argument(
        '--seed', '-S', type=int,
        help="""Create a random seed for python. (default: %(default)s)""")

    args = arg_parser.parse_args()

    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    imputable_values(ARGS)

    finished()
