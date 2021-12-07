#!/usr/bin/env python3
"""Find "best" labels from ensembles of OCR results of each label."""
import argparse
import textwrap
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from .pylib import db
from .pylib import line_align_py as la  # type: ignore
from .pylib import line_align_subs
from .pylib import ocr_results
from .pylib.spell_well import SpellWell


def build_labels(args):
    """Build labels from ensembles of OCR output."""
    db.create_cons_table(args.database)
    line_align = la.LineAlign(line_align_subs.SUBS)

    limit = args.limit if args.limit else 999_999_999

    ocr_runs = get_ocr_runs(args.database, args.ocr_runs)

    ocr_labels = {}
    for lb in db.select_labels(args.database, classes=args.classes):
        ocr_labels[lb["label_id"]] = dict(lb)

    ocr_fragments = get_ocr_fragments(
        ocr_labels, args.database, args.ocr_runs, args.classes
    )

    spell_well = SpellWell()
    batch = []
    for i, (label_id, fragments) in tqdm(enumerate(ocr_fragments.items())):
        if i == limit:
            break
        text = build_label_text(fragments, spell_well, line_align)
        batch.append(
            {
                "label_id": label_id,
                "cons_run": args.cons_run,
                "ocr_run": ocr_runs,
                "cons_text": text,
            }
        )

    db.insert_cons(args.database, batch)


def build_label_text(ocr_fragments, spell_well, line_align):
    """Build a label text from a ensemble of OCR output."""
    text = []

    ocr_fragments = ocr_results.filter_boxes(ocr_fragments)
    lines = ocr_results.get_lines(ocr_fragments)

    for line in lines:
        copies = ocr_results.get_copies(line)

        if len(copies) <= 1:
            continue

        ln = consensus(copies, line_align, spell_well)
        # ln = ocr_results.choose_best_copy(copies, spell_well)

        ln = ocr_results.substitute(ln)
        ln = ocr_results.spaces(ln, spell_well)
        ln = ocr_results.correct(ln, spell_well)

        text.append(ln)

    return "\n".join(text)


def consensus(copies, line_align, spell_well):
    """Build a multiple-alignment consensus sequence from the copies of lines."""
    copies = ocr_results.sort_copies(copies, line_align)
    aligned = ocr_results.align_copies(copies, line_align)
    cons = ocr_results.consensus(aligned, spell_well)
    return cons


def get_ocr_fragments(ocr_labels, database, ocr_runs=None, classes=None):
    """Read OCR records and group them by label."""
    ocr = [dict(o) for o in db.select_ocr(database, ocr_runs, classes)]
    records = defaultdict(list)
    for o in ocr:
        if o["label_id"] in ocr_labels:
            records[o["label_id"]].append(o)
    return records


def get_ocr_runs(database, ocr_runs):
    """Get the OCR runs included in this cons_run."""
    if not ocr_runs:
        ocr_runs = [r["ocr_run"] for r in db.get_ocr_runs(database)]
    ocr_runs = ",".join(ocr_runs)
    return ocr_runs


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """
        Build a single "best" label from an ensemble of OCR outputs for
        every selected label. An ensemble is a set of OCR outputs of
        the same label using various image processing pipelines and OCR
        engines. They are grouped by OCR "runs"."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Path to the digi-leap database.""",
    )

    default = datetime.now().isoformat(sep="_", timespec="seconds")
    arg_parser.add_argument(
        "--cons-run",
        default=default,
        help="""Name the consensus construction run. (default: %(default)s).""",
    )

    arg_parser.add_argument(
        "--ocr-runs",
        type=str,
        nargs="*",
        help="""Which OCR runs contain the label ensembles.""",
    )

    arg_parser.add_argument(
        "--classes",
        choices=["Barcode", "Handwritten", "Typewritten", "Both"],
        type=str,
        nargs="*",
        default=["Typewritten"],
        help="""Keep labels if they fall into any of these categories.
            (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--limit",
        type=int,
        help="""Limit the input to this many records.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = parse_args()
    build_labels(ARGS)
