#!/usr/bin/env python3
"""Get plant taxon names from ITIS."""

import re
import sqlite3
import string
import textwrap
from argparse import ArgumentParser, Namespace
from pathlib import Path

import pandas as pd

from digi_leap.pylib.config import Config
import digi_leap.pylib.log as log

NAMES = """ var subvar sp ssp subf """.split()
PUNCT = re.escape(string.punctuation)
SPLIT = re.compile(rf"[\s{PUNCT}]+")


def get_itis_data(args):
    """Get the data."""
    names = set(NAMES)
    names |= taxonomic_names(args.itis_db)
    names |= people_names(args.itis_db)
    names = filter_names(names)
    for name in names:
        print(name)


def people_names(itis_db: Path) -> set[str]:
    """Get name parts."""
    sql = """
        select expert as name from experts
        union select reference_author from publications
        union select shortauthor from strippedauthor
        union select short_author from taxon_authors_lkp
        """
    with sqlite3.connect(itis_db) as cxn:
        df = pd.read_sql(sql, cxn)
    names = df["name"].str.lower().unique()

    parts = set()
    for name in names:
        parts |= {
            x for w in SPLIT.split(name) if (x := w.strip()) and not re.search(r"\d", x)
        }

    return parts


def taxonomic_names(itis_db: Path) -> set[str]:
    """Get taxonomic names."""
    sql = """
    select unit_name1 as name from taxonomic_units where unit_name1 is not null
    union select unit_name2 from taxonomic_units where unit_name2 is not null
    union select unit_name3 from taxonomic_units where unit_name3 is not null
    union select unit_name4 from taxonomic_units where unit_name4 is not null
    """
    with sqlite3.connect(itis_db) as cxn:
        df = pd.read_sql(sql, cxn)
    df["name"] = df["name"].str.lower()

    names = {x for w in df["name"] if (x := w.strip())}
    return names


def filter_names(names: set[str]) -> list[str]:
    """Only put new names into the output list."""
    # vocab = enchant.Dict(lang)
    # names = [n for n in names if not vocab.check(n)]
    names = [n for n in names if len(n) > 1]
    names = sorted(names)
    return names


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """
    Create a vocabulary file of all plant taxon names.
    """
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    defaults = Config().module_defaults()

    arg_parser.add_argument(
        "--itis-db",
        default=defaults["itis_db"],
        type=Path,
        help="""The ITIS SQLite3 database. (default: %(default)s)""",
    )

    # arg_parser.add_argument(
    #     "--lang",
    #     default=module_defaults['lang'],
    #     help="""Which language to use. (default: %(default)s)""",
    # )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    get_itis_data(ARGS)

    log.finished()
