#!/usr/bin/env python3
import argparse
import logging
import re
import textwrap
from pathlib import Path

from pylib import log


def main():
    log.started()
    args = parse_args()

    new = []

    paths = sorted(args.sheet_dir.glob("*"))
    for src in paths:
        stem = re.sub(r"[^\w-]", "_", src.stem)
        dst = src.with_name(stem + src.suffix)

        if not dst.exists():
            src.rename(dst)
            new.append(dst)
        elif src == dst:
            new.append(src)
        else:
            logging.error(f"Could not rename {src} because {dst} already exists.")

    if args.sheet_csv:
        with open(args.sheet_csv, "w") as out:
            out.write("path\n")
            for path in sorted(new):
                out.write(f"{path}\n")

    log.finished()


def parse_args():
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Fix odd file names and create a CSV file of them.
            Backup your input images before using.
            """
        ),
    )

    arg_parser.add_argument(
        "--sheet-dir",
        type=Path,
        metavar="PATH",
        required=True,
        help="""The sheet images are in this directory.""",
    )

    arg_parser.add_argument(
        "--sheet-csv",
        type=Path,
        metavar="PATH",
        help="""Output the paths of sheets to this CSV file.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
