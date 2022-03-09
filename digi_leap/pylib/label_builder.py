"""Find "best" labels from ensembles of OCR results of each label."""
from collections import defaultdict

from tqdm import tqdm

from . import db
from . import ocr_results
from .line_align import line_align_py as la  # type: ignore
from .line_align import line_align_subs
from .spell_well import spell_well as sw


def build_labels(args):
    """Build labels from ensembles of OCR output."""
    run_id = db.insert_run(args)
    db.create_consensus_table(args.database)
    line_align = la.LineAlign(line_align_subs.SUBS)

    limit = args.limit if args.limit else float("inf")

    frags = get_ocr_fragments(args.database, args.ocr_set)

    spell_well = sw.SpellWell()
    batch = []

    for i, (label_id, fragments) in tqdm(enumerate(frags.items()), total=len(frags)):
        if i >= limit:
            break
        text = build_label_text(fragments, spell_well, line_align)
        batch.append(
            {
                "label_id": label_id,
                "cons_set": args.cons_set,
                "ocr_set": args.ocr_set,
                "cons_text": text,
            }
        )

    db.insert_consensus(args.database, batch)
    db.update_run_finished(args.database, run_id)


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


def get_ocr_fragments(database, ocr_set):
    """Read OCR records and group them by label."""
    frags = defaultdict(list)
    for ocr in db.select_ocr(database, ocr_set):
        frags[ocr["label_id"]].append(ocr)
    return frags
