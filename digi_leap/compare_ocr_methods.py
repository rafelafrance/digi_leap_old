#!/usr/bin/env python3
import argparse
import sqlite3
import textwrap
import warnings
from pathlib import Path

import cppimport.import_hook  # noqa: F401
import pytesseract
from PIL import Image
from pylib import log
from pylib.label_builder import label_builder
from pylib.ocr import label_transformer
from pylib.ocr import ocr_runner

from digi_leap.pylib.db import db
from digi_leap.pylib.label_builder.line_align import line_align_py  # noqa
from digi_leap.pylib.label_builder.line_align import line_align_subs
from digi_leap.pylib.label_builder.spell_well import spell_well as sw


def main():
    log.started()
    args = parse_args()

    with sqlite3.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        sql = "select * from gold_standard where gold_set = ?"
        golden = [g for g in cxn.execute(sql, (args.gold_set,))]

        scores = get_scores(args, golden)
        output_scores(scores)

        db.update_run_finished(cxn, run_id)

    log.finished()


def get_scores(args, golden):
    scores = []

    spell_well = sw.SpellWell()
    line_align = line_align_py.LineAlign(line_align_subs.SUBS)

    for gold in golden:
        scores.append(score_tess(args, line_align, gold))
        scores.append(score_tess(args, line_align, gold, pipeline="deskew"))
        scores.append(score_tess(args, line_align, gold, pipeline="binarize"))
        scores.append(score_tess(args, line_align, gold, pipeline="denoise"))

        scores.append(score_easy(args, line_align, gold))
        scores.append(score_easy(args, line_align, gold, pipeline="deskew"))
        scores.append(score_easy(args, line_align, gold, pipeline="binarize"))
        scores.append(score_easy(args, line_align, gold, pipeline="denoise"))

        # TODO: Cache the OCR fragments
        pipelines = """ deskew binarize """.split()

        scores.append(
            score_label_builder(
                args, line_align, gold, pipelines, spell_well, post=False
            )
        )

        scores.append(
            score_label_builder(
                args, line_align, gold, pipelines, spell_well, post=True
            )
        )

        pipelines = """ deskew binarize denoise """.split()

        scores.append(
            score_label_builder(
                args, line_align, gold, pipelines, spell_well, post=False
            )
        )

        scores.append(
            score_label_builder(
                args, line_align, gold, pipelines, spell_well, post=True
            )
        )

    return scores


def score_easy(args, line_align, gold, pipeline=""):
    image = read_label(gold, pipeline)
    text = ocr_runner.EngineConfig.easy_ocr.readtext(
        image, blocklist=ocr_runner.EngineConfig.char_blacklist, detail=0
    )
    text = " ".join(text)
    return new_score_rec(args, line_align, gold, pipeline, "easy", text)


def score_tess(args, line_align, gold, pipeline=""):
    image = read_label(gold, pipeline)
    text = pytesseract.image_to_string(
        image, config=ocr_runner.EngineConfig.tess_config
    )
    return new_score_rec(args, line_align, gold, pipeline, "tesseract", text)


def score_label_builder(args, line_align, gold, pipelines, spell_well, post):
    ocr_fragments = []
    for pipeline in pipelines:
        image = read_label(gold, pipeline)
        ocr_fragments += ocr_runner.easyocr_engine(image)
        ocr_fragments += ocr_runner.tesseract_engine(image)

    text = label_builder.build_label_text(ocr_fragments, spell_well, line_align)

    pipeline = ",".join(pipelines)
    engines = "easy,tesseract"
    action = "label_builder" if post else "consensus"
    return new_score_rec(args, line_align, gold, pipeline, engines, text, action)


def new_score_rec(args, line_align, gold, pipeline, engine, text, action="simple"):
    return {
        "gold_id": gold["gold_id"],
        "gold_set": args.gold_set,
        "score_set": args.score_set,
        "action": action,
        "engine": engine,
        "pipelines": pipeline,
        "text": text,
        "levenshtein": line_align.levenshtein(gold["gold_text"], text),
    }


def read_label(gold, pipeline=""):
    with warnings.catch_warnings():  # Turn off EXIF warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        image = Image.open(gold["path"])

    if pipeline:
        image = label_transformer.transform_label(pipeline, image)

    return image


def output_scores(scores):
    print(scores)


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
        help="""Notes about this run.""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    main()
