#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import consts
from pylib import fonts
from pylib.label_builder.line_align import char_sub_matrix as matrix


def main():
    args = parse_args()
    matrix.add_chars(args)


def parse_args() -> argparse.Namespace:
    description = """Add characters to the Line Align utility's character substitution
        matrix. The matrix has the characters along the row and column headers and
        each cell value has a value that is a coarse approximation of how visually
        similar the two characters are."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--char-set",
        default="default",
        metavar="NAME",
        help="""Update this character set matrix. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--chars",
        default=consts.CHARS,
        metavar="CHARS",
        help="""A string containing the characters to add to the matrix. You may want
            to add a space character but other whitespace characters are not useful.
            Characters here will replace those in the char-set. Default includes a
            space. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--font",
        type=Path,
        metavar="PATH",
        default=fonts.FONT2,
        help="""A true type font file to use for calculations.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--font-size",
        type=int,
        metavar="SIZE",
        default=fonts.BASE_FONT_SIZE,
        help="""The font size to use for calculations. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
