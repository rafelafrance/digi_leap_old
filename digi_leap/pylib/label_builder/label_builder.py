"""Find "best" labels from ensembles of OCR results of each label."""
import multiprocessing
from collections import defaultdict
from itertools import chain
from multiprocessing import Pool

from tqdm import tqdm

from . import ocr_results
from .. import utils
from ..db import db
from .line_align import char_sub_matrix as subs
from .line_align import line_align_py as la  # noqa type: ignore
from .spell_well import spell_well as spell


def build_labels(args):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        multiprocessing.set_start_method("spawn")

        frags = get_ocr_fragments(cxn, args.ocr_set)
        batches = utils.dict_chunks(frags, args.batch_size)

        matrix = subs.select_char_sub_matrix(args.database, args.char_set)

        results = []
        with Pool(processes=args.workers) as pool, tqdm(total=len(batches)) as bar:
            for batch in batches:
                results.append(
                    pool.apply_async(
                        build_batch,
                        args=(batch, args.consensus_set, args.ocr_set, matrix),
                        callback=lambda _: bar.update(),
                    )
                )
            results = [r.get() for r in results]

        results = list(chain(*list(results)))

        db.execute(
            cxn,
            "delete from consensuses where consensus_set = ?",
            (args.consensus_set,),
        )
        db.canned_insert("consensuses", cxn, results)
        db.update_run_finished(cxn, run_id)


def build_batch(labels, consensus_set, ocr_set, matrix):
    spell_well = spell.SpellWell()
    line_align = la.LineAlign(matrix)

    batch: list[dict] = []

    for label_id, fragments in labels.items():
        text = build_label_text(fragments, spell_well, line_align)
        text = post_process_text(text, spell_well)
        batch.append(
            {
                "label_id": label_id,
                "consensus_set": consensus_set,
                "ocr_set": ocr_set,
                "consensus_text": text,
            }
        )
    return batch


def build_label_text(ocr_fragments, spell_well, line_align):
    text = []

    ocr_fragments = ocr_results.filter_boxes(ocr_fragments)
    lines = ocr_results.get_lines(ocr_fragments)

    for line in lines:
        copies = ocr_results.get_copies(line)

        if len(copies) <= 1:
            continue

        ln = consensus(copies, line_align, spell_well)
        # ln = ocr_results.choose_best_copy(copies, spell_well)

        text.append(ln)

    return "\n".join(text)


def post_process_text(text, spell_well):
    lines = []
    for ln in text.splitlines():
        ln = ocr_results.substitute(ln)
        ln = ocr_results.add_spaces(ln, spell_well)
        ln = ocr_results.remove_spaces(ln, spell_well)
        ln = ocr_results.correct(ln, spell_well)
        lines.append(ln)
    return "\n".join(lines)


def consensus(copies, line_align, spell_well):
    """Build a multiple-alignment consensus sequence from the copies of lines."""
    copies = ocr_results.sort_copies(copies, line_align)
    aligned = ocr_results.align_copies(copies, line_align)
    cons = ocr_results.consensus(aligned, spell_well)
    return cons


def get_ocr_fragments(cxn, ocr_set):
    frags = defaultdict(list)

    for ocr in db.canned_select("ocr", cxn, ocr_set=ocr_set):
        frags[ocr["label_id"]].append(ocr)

    return frags
