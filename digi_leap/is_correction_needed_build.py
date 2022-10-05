#!/usr/bin/env python3
"""Build an expedition to determine the quality of label finder output."""
import argparse
import textwrap
from pathlib import Path

from pylib.ocr.is_correction_needed import build_expedition
from traiter import log


def main():
    log.started()
    args = parse_args()
    build_expedition.build(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Build the "Is Correction Needed?" expedition.  (-RrDdbnp)"""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--expedition-dir",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Place expedition files in this directory.""",
    )

    arg_parser.add_argument(
        "--gold-set",
        required=True,
        metavar="NAME",
        help="""Get labels from this gold set.""",
    )

    arg_parser.add_argument(
        "-R",
        "--none-easyocr",
        action="store_true",
        help="""Add a step to the OCR pipeline that runs EasyOCR without image
            manipulation.""",
    )

    arg_parser.add_argument(
        "-r",
        "--none-tesseract",
        action="store_true",
        help="""Add a step to the OCR pipeline that runs Tesseract without image
            manipulation.""",
    )

    arg_parser.add_argument(
        "-D",
        "--deskew-easyocr",
        action="store_true",
        help="""Add a step to the OCR pipeline that deskews the label image before
            running EasyOCR.""",
    )

    arg_parser.add_argument(
        "-d",
        "--deskew-tesseract",
        action="store_true",
        help="""Add a step to the OCR pipeline that deskews the label image before
            running Tesseract.""",
    )

    arg_parser.add_argument(
        "-B",
        "--binarize-easyocr",
        action="store_true",
        help="""Add a step to the OCR pipeline that binarizes the label image before
            running EasyOCR.""",
    )

    arg_parser.add_argument(
        "--binarize-tesseract",
        "-b",
        action="store_true",
        help="""Add a step to the OCR pipeline that binarizes the label image before
            running Tesseract.""",
    )

    arg_parser.add_argument(
        "--denoise-easyocr",
        "-N",
        action="store_true",
        help="""Add a step to the OCR pipeline that denoises the label image before
            running EasyOCR.""",
    )

    arg_parser.add_argument(
        "-n",
        "--denoise-tesseract",
        action="store_true",
        help="""Add a step to the OCR pipeline that denoises the label image before
            running Tesseract.""",
    )

    arg_parser.add_argument(
        "-p",
        "--post-process",
        action="store_true",
        help="""Add a step to the OCR pipeline that post-processes the OCR text
            sequence with a spell checker etc.""",
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
