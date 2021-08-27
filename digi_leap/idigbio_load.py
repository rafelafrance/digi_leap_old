#!/usr/bin/env python
"""Load iDigBio Data into a database."""

import argparse
import sqlite3
import textwrap
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import tqdm

import pylib.const as const
import pylib.log as log


@dataclass
class CsvParams:
    """How to process the CSV data before putting it into the DB."""

    file_name: str
    keep_cols: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    headers: list[str] = field(default_factory=list)
    drops: list[str] = field(default_factory=list)
    renames: dict[str, str] = field(default_factory=dict)

    def __init__(self, zip_file, file_name, keep_cols, filters):
        self.file_name = file_name
        self.keep_cols = keep_cols
        self.filters = filters
        self.headers = self.get_csv_headers(zip_file)
        self.drops = self.get_columns_to_drop()
        self.renames = self.get_column_renames()

    def get_csv_headers(self, zip_file):
        """Get the headers from the CSV file in the zipped snapshot."""
        with zipfile.ZipFile(zip_file) as zippy:
            with zippy.open(self.file_name) as csv_file:
                headers = csv_file.readline()
        return [h.decode().strip() for h in sorted(headers.split(b","))]

    def get_columns_to_drop(self):
        """Get columns to drop."""
        if not self.keep_cols:
            return []
        keeps = set(self.keep_cols)
        drops = [h for h in self.headers if h not in keeps]
        return drops

    def get_column_renames(self):
        """Rename column names so they'll work in sqlite3."""
        drops = set(self.drops)
        renames = {}
        used = set()

        for header in [h for h in self.headers if h not in drops]:
            col = header
            suffix = 0
            while col.casefold() in used:
                suffix += 1
                col = f"{header}_{str(suffix)}"
            used.add(col.casefold())
            renames[header] = col

        return {k: renames[k] for k in self.keep_cols} if self.keep_cols else renames


@dataclass
class DbParams:
    """Parameters for how to put the data into the DB."""

    database: Path
    table_name: str
    append_to: bool
    batch_size: int


def load_data(args):
    """Load the data."""
    csv_params = CsvParams(args.zip_file, args.csv_file, args.keep_col, args.filter)

    if args.column_names:
        for header in csv_params.headers:
            print(f"[{header}]")
        return

    db_params = DbParams(
        args.database, args.table_name, args.append_to, args.batch_size
    )

    insert(args.zip_file, csv_params, db_params)


def insert(zip_file, csv_params, db_params):
    """Insert data from the CSV file into an SQLite3 database."""
    with sqlite3.connect(db_params.database) as cxn:
        with zipfile.ZipFile(zip_file) as zipped:
            with zipped.open(csv_params.file_name) as in_file:

                reader = pd.read_csv(
                    in_file,
                    dtype=str,
                    keep_default_na=False,
                    chunksize=db_params.batch_size,
                )

                if_exists = "append" if db_params.append_to else "replace"

                for df in tqdm.tqdm(reader):
                    # TODO: Slows things down but not doing it causes a memory leak
                    df = df.copy()

                    if csv_params.filters:
                        for f in csv_params.filters:
                            regex, col = f.split("@")
                            mask = df[col].str.contains(regex, regex=True, case=False)
                            df = df.loc[mask, :]

                    if csv_params.drops:
                        df = df.drop(columns=csv_params.drops)

                    df = df.rename(columns=csv_params.renames)
                    df = df.reindex(columns=csv_params.renames.values())

                    df.to_sql(
                        db_params.table_name, cxn, if_exists=if_exists, index=False
                    )

                    del df  # More memory leak protection but not enough on its own

                    if_exists = "append"


def parse_args():
    """Process command-line arguments."""
    description = """
        Load iDigBio Data.

        The files in the iDigBio snapshot is too big to work with easily on a laptop.
        So, we extract one CSV file from them and then create a database table from
        that CSV. Later on we will sample this data several times before eventually
        deleting it.
    """
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    defaults = const.get_config()

    arg_parser.add_argument(
        "--database",
        default=defaults["database"],
        type=Path,
        help="""Path to the output database. This is a temporary database that
            will later be sampled and then deleted.""",
    )

    arg_parser.add_argument(
        "--zip-file",
        default=defaults["zip_file"],
        type=Path,
        help="""The zip file containing the iDigBio snapshot.""",
    )

    arg_parser.add_argument(
        "--csv-file",
        default=defaults["csv_file"],
        type=Path,
        help="""The --zip-file itself contains several files. This is the file we
            are extracting for data. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--column-names",
        action="store_true",
        help="""Dump the column names and exit.""",
    )

    arg_parser.add_argument(
        "--table-name",
        default=defaults["table_name"],
        help="""Write the output to this table. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--keep-col",
        action="append",
        help="""Columns to keep from the CSV file. You may use this argument more
            than once.""",
    )

    arg_parser.add_argument(
        "--filter",
        action="append",
        help="""Records must contain this value in the given field. You may use
            this argument more than once. The format is regex@column. For example
            --filter=plant@dwc:kingdom will only choose records that have 'plant'
            somewhere in the 'dwc:kingdom' field and --filter=.@dwc:scientificName
            will look for a non-blank 'dwc:scientificName' field. You may filter
            on columns that will not be in the output table.""",
    )

    arg_parser.add_argument(
        "--append-to",
        action="store_true",
        help="""Are we appending to the table or creating a new one. The default is
            to create a new table.""",
    )

    arg_parser.add_argument(
        "--batch-size",
        type=int,
        default=defaults["batch_size"],
        help="""The number of lines we read from the CSV file at a time. This
            is mostly used to shorten iterations for debugging.
            (default: %(default)s)""",
    )

    args = arg_parser.parse_args()

    if not args.table_name:
        args.table_name = args.csv_file.split(".")[0]

    args.filter = args.filter if args.filter else []

    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    load_data(ARGS)

    log.finished()
