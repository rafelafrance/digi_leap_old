"""Find "best" labels from ensembles of OCR results of each label."""
from collections import defaultdict

from tqdm import tqdm

from . import db
from . import line_align_py as la  # type: ignore
from . import ocr_results
from .line_align import line_align_subs
from .spell_well import spell_well as sw


def build_labels(args):
    """Build labels from ensembles of OCR output."""
    db.create_consensus_table(args.database)
    line_align = la.LineAlign(line_align_subs.SUBS)

    limit = args.limit if args.limit else float("inf")

    ocr_sets = get_ocr_sets(args.database, args.ocr_sets)

    ocr_labels = {}
    for lb in db.select_labels(args.database, classes=args.classes):
        ocr_labels[lb["label_id"]] = dict(lb)

    ocr_fragments = get_ocr_fragments(
        ocr_labels, args.database, args.ocr_sets, args.classes
    )

    spell_well = sw.SpellWell()
    batch = []
    for i, (label_id, fragments) in tqdm(enumerate(ocr_fragments.items())):
        if i == limit:
            break
        text = build_label_text(fragments, spell_well, line_align)
        batch.append(
            {
                "label_id": label_id,
                "cons_set": args.cons_set,
                "ocr_set": ocr_sets,
                "cons_text": text,
            }
        )

    db.insert_consensus(args.database, batch)


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


def get_ocr_fragments(ocr_labels, database, ocr_sets=None, classes=None):
    """Read OCR records and group them by label."""
    ocr = [dict(o) for o in db.select_ocr(database, ocr_sets, classes)]
    records = defaultdict(list)
    for o in ocr:
        if o["label_id"] in ocr_labels:
            records[o["label_id"]].append(o)
    return records


def get_ocr_sets(database, ocr_sets):
    """Get the OCR runs included in this cons_set."""
    if not ocr_sets:
        ocr_sets = [r["ocr_set"] for r in db.get_ocr_sets(database)]
    ocr_sets = ",".join(ocr_sets)
    return ocr_sets
