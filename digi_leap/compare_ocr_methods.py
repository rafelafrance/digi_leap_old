#!/pip install voilausr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import log

from digi_leap.pylib.ocr.ocr_compare import compare_methods


def main():
    log.started()
    args = parse_args()

    compare_methods(args)

    log.finished()


def parse_args() -> argparse.Namespace:
    description = """
        Compare various OCR engines and image/text enhancement methods.
        """

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        "--db",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--gold-set",
        required=True,
        metavar="NAME",
        help="""Use this as the gold standard of expert transcribed labels.""",
    )

    arg_parser.add_argument(
        "--score-set",
        required=True,
        metavar="NAME",
        help="""Save score results to this set.""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run. Enclose them in quotes.""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    main()
