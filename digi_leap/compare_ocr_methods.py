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
from pylib.ocr import engine_runner as er
from pylib.ocr import label_transformer as lt

from digi_leap.pylib.db import db
from digi_leap.pylib.label_builder.line_align import line_align_py  # noqa


def main():
    log.started()
    args = parse_args()

    with sqlite3.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)
        aligner = line_align_py.LineAlign()

        sql = "select * from gold_standard where gold_set = ?"
        golden = [g for g in cxn.execute(sql, (args.gold_set,))]

        scores = get_scores(aligner, golden)
        output_scores(scores)

        db.update_run_finished(cxn, run_id)

    log.finished()


def get_scores(aligner, golden):
    scores = []

    for gold in golden:
        scores.append(score_tess(aligner, gold))
        scores.append(score_tess(aligner, gold, pipeline="deskew"))
        scores.append(score_tess(aligner, gold, pipeline="binarize"))
        scores.append(score_tess(aligner, gold, pipeline="denoise"))

        scores.append(score_easy(aligner, gold))
        scores.append(score_easy(aligner, gold, pipeline="deskew"))
        scores.append(score_easy(aligner, gold, pipeline="binarize"))
        scores.append(score_easy(aligner, gold, pipeline="denoise"))

        scores.append(score_consensus(aligner, gold))
        scores.append(score_label_builder(aligner, gold))

    return scores


def score_easy(aligner, gold, pipeline=""):
    image = read_label(gold, pipeline)

    text = er.EngineConfig.easy_ocr.readtext(
        image, blocklist=er.EngineConfig.char_blacklist, detail=0
    )
    text = " ".join(text)

    score = {
        "engine": "easy",
        "pipeline": pipeline,
        "text": text,
        "levenshtein": aligner.levenshtein(gold["gold_text"], text),
    }

    return score


def score_tess(aligner, gold, pipeline=""):
    image = read_label(gold, pipeline)
    text = pytesseract.image_to_data(image, config=er.EngineConfig.tess_config)

    score = {
        "engine": "tesseract",
        "pipeline": pipeline,
        "text": text,
        "levenshtein": aligner.levenshtein(gold["gold_text"], text),
    }

    return score


def score_consensus(aligner, gold):
    text = ""
    score = aligner.levenshtein(gold["gold_text"], text)
    return score


def score_label_builder(aligner, gold):
    text = ""
    score = aligner.levenshtein(gold["gold_text"], text)
    return score


def read_label(gold, pipeline=""):
    with warnings.catch_warnings():  # Turn off EXIF warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        image = Image.open(gold["path"])

    if pipeline:
        image = lt.transform_label(pipeline, image)

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
