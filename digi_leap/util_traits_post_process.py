#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import validate_args
from pylib.builder import label_builder
from pylib.db import db
from tqdm import tqdm
from traiter.pylib import log
from traiter.pylib import util
from traiter.pylib.spell_well import SpellWell


def main():
    log.started()
    args = parse_args()
    sql = """update ocr_texts set ocr_text = :ocr_text where label_id = :label_id"""
    spell_well = SpellWell()

    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        records = db.canned_select(cxn, "ocr_texts", ocr_set=args.ocr_set)

        for rec in tqdm(records):
            text = util.shorten(rec["ocr_text"])
            text = label_builder.post_process_text(text, spell_well)
            db.update(cxn, sql, ocr_text=text, label_id=rec["label_id"])

        db.update_run_finished(cxn, run_id)

    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Post-process an OCR set again."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--in-ocr-set",
        required=True,
        metavar="NAME",
        help="""Process this OCR set.""",
    )

    arg_parser.add_argument(
        "--out-ocr-set",
        required=True,
        metavar="NAME",
        help="""Process this OCR set.""",
    )

    args = arg_parser.parse_args()
    validate_args.validate_ocr_set(args.database, args.ocr_set)
    return args


if __name__ == "__main__":
    main()
