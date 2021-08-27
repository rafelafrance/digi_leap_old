#!/usr/bin/env python
"""Load iDigBio Data into a database."""

import argparse
import re
import sqlite3
import textwrap
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import tqdm

import pylib.log as log
from pylib.config import Configs


@dataclass
class CsvParams:
    """How to process the CSV data before putting it into the DB."""

    file_name: str
    col_filters: list[str] = field(default_factory=list)
    row_filters: list[str] = field(default_factory=list)
    headers: list[str] = field(default_factory=list)
    drops: list[str] = field(default_factory=list)
    renames: dict[str, str] = field(default_factory=dict)

    def __init__(self, zip_file, file_name, col_filters, row_filters):
        self.file_name = file_name
        self.col_filters = col_filters
        self.row_filters = row_filters
        self.headers = self.get_csv_headers(zip_file)
        self.renames = self.get_column_renames()
        self.drops = self.get_columns_to_drop()

    def get_csv_headers(self, zip_file):
        """Get the headers from the CSV file in the zipped snapshot."""
        with zipfile.ZipFile(zip_file) as zippy:
            with zippy.open(self.file_name) as csv_file:
                headers = csv_file.readline()
        headers = [h.decode() for h in headers.split(b",")]
        headers = [n for h in sorted(headers) if (n := h.strip())]
        return headers

    def get_columns_to_drop(self):
        """Get columns to drop."""
        keeps = []
        for header in self.headers:
            for filter_ in self.col_filters:
                if re.search(filter_, header):
                    keeps.append(header)
                    break
        drops = [h for h in self.headers if h not in keeps]
        return drops

    def get_column_renames(self):
        """Rename columns so they'll work in sqlite3."""
        drops = set(self.drops)
        rename = {}
        used = set()

        for header in [h for h in self.headers if h not in drops]:
            new = header
            suffix = 0
            while new.casefold() in used:
                suffix += 1
                new = f"{header}_{str(suffix)}"
            used.add(new.casefold())
            rename[header] = new
        return rename


@dataclass
class DbParams:
    """Parameters for how to put the data into the DB."""

    database: Path
    table_name: str
    append_to: bool
    batch_size: int


def load_data(args):
    """Load the data."""
    csv_params = CsvParams(
        args.zip_file, args.csv_file, args.col_filters, args.row_filters
    )

    if args.show_columns:
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

                    if csv_params.row_filters:
                        for f in csv_params.row_filters:
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
        that CSV."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    configs = Configs()
    defaults = configs.module_defaults()

    arg_parser.add_argument(
        "--database",
        default=defaults["database"],
        type=Path,
        help="""Path to the output SQLite3 database.""",
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
            are CSV file inside of the zip file that contains the data.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--show-columns",
        action="store_true",
        help="""Show the column names and exit.""",
    )

    arg_parser.add_argument(
        "--table-name",
        default=defaults["table_name"],
        help="""Write the output to this table. (default: %(default)s)""",
    )

    default = ' '.join(configs.default_list('col_filters'))
    arg_parser.add_argument(
        "--col-filters",
        default=configs.default_list('col_filters'),
        nargs="*",
        help=f"""Column names must match any of these patterns or the column will not
            get into the database. You may add more than one filter. The filters may
            be a constant or a regex. For example, --col-filters=dwc will match all
            columns with 'dwc' in the column name and --col-filters=. will match all
            non-blank columns. Column names only need to match one of the filters to
            get into the database. It's an 'or' condition. (default: {default})""",
    )

    default = ' '.join(configs.default_list('row_filters'))
    arg_parser.add_argument(
        "--row-filters",
        default=configs.default_list('row_filters'),
        nargs="*",
        help=f"""Rows must contain these patterns in the given fields. You may use
            more than one filter. The format is regex@column. For example,
            --row-filters=plant@dwc:kingdom will only choose rows that have 'plant'
            somewhere in the 'dwc:kingdom' field and --row-filters=.@dwc:scientificName
            will look for a non-blank 'dwc:scientificName' field. If you use more than
            one filter the row must match all of the filters to get into the
            database. It's an 'and' condition. (default: {default})""",
    )

    arg_parser.add_argument(
        "--append-to",
        action="store_true",
        help="""Are we appending to the database table or creating a new one. The
            default is to create a new table.""",
    )

    arg_parser.add_argument(
        "--batch-size",
        type=int,
        default=defaults["batch_size"],
        help="""The number of lines we read from the CSV file at a time.
            (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    log.started()

    ARGS = parse_args()
    load_data(ARGS)

    log.finished()
