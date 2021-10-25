"""Find "best" labels from ensembles of OCR results of each label."""
from collections import defaultdict
from datetime import datetime

from tqdm import tqdm

from digi_leap.pylib import db
from digi_leap.pylib import ocr_results


def build_labels(args):
    """Build labels from ensembles of OCR output."""
    db.create_cons_table(args.database)

    limit = args.limit if args.limit else 999_999_999

    cons_run = args.cons_run
    if not cons_run:
        cons_run = datetime.now().isoformat(sep="_", timespec="seconds")

    ocr_runs = get_ocr_runs(args.database, args.ocr_runs)

    ocr_labels = {
        lb["label_id"]: dict(lb)
        for lb in db.select_labels(args.database, classes=args.classes)
    }

    ocr_fragments = get_ocr_fragments(
        ocr_labels, args.database, args.ocr_runs, args.classes
    )

    batch = []
    for i, (label_id, fragments) in tqdm(enumerate(ocr_fragments.items())):
        if i == limit:
            break
        label = ocr_labels[label_id]
        text = build_label_text(label, fragments)
        batch.append(
            {
                "label_id": label_id,
                "cons_run": cons_run,
                "ocr_run": ocr_runs,
                "cons_text": text,
            }
        )

    db.insert_cons(args.database, batch)


def build_label_text(label, ocr_fragments):
    """Build a label text from a ensemble of OCR output."""
    text = []

    ocr_fragments = ocr_results.filter_boxes(ocr_fragments, label["height"])
    lines = ocr_results.get_lines(ocr_fragments)

    for line in lines:
        copies = ocr_results.get_copies(line)

        if len(copies) <= 1:
            continue

        ln = consensus(copies)
        # ln = ocr_results.choose_best_copy(copies)

        ln = ocr_results.substitute(ln)
        ln = ocr_results.spaces(ln)
        text.append(ln)

    return "\n".join(text)


def consensus(copies):
    """Build a multiple-alignment consensus sequence from the copies of lines."""
    copies = ocr_results.sort_copies(copies)
    aligned = ocr_results.align_copies(copies)
    cons = ocr_results.consensus(aligned)
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
    ocr_runs = ocr_runs if ocr_runs else [r[0] for r in db.get_ocr_runs(database)]
    ocr_runs = ",".join(ocr_runs)
    return ocr_runs
