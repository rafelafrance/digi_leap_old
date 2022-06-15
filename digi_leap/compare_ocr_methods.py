#!/usr/bin/env python3
import argparse
import sqlite3
import textwrap
import warnings
from pathlib import Path

import cppimport.import_hook  # noqa pylint: disable=unused-import
import pandas as pd
import pytesseract
from PIL import Image
from pylib import log
from pylib.db import db
from pylib.label_builder import label_builder
from pylib.label_builder.line_align import line_align_py  # noqa
from pylib.label_builder.line_align import line_align_subs
from pylib.label_builder.spell_well import spell_well as sw
from pylib.ocr import label_transformer
from pylib.ocr import ocr_runner


def main():
    log.started()
    args = parse_args()

    with sqlite3.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        sql = "select * from gold_standard where gold_set = ?"
        golden = cxn.execute(sql, (args.gold_set,))

        scores = get_scores(args, golden)
        output_scores(args, cxn, scores)

        db.update_run_finished(cxn, run_id)

    log.finished()


def get_scores(args, golden):
    scores = []

    spell_well = sw.SpellWell()
    line_align = line_align_py.LineAlign(line_align_subs.SUBS)

    for gold in golden:
        images = {}  # Cache the processed images

        # Test simple OCR of images
        for pipeline in ["", "deskew", "binarize", "denoise"]:
            image = read_label(gold, pipeline)
            images[pipeline] = image
            scores.append(tess_score(args, line_align, gold, image, pipeline=pipeline))
            scores.append(easy_score(args, line_align, gold, image, pipeline=pipeline))

        # Cache the ocr fragments
        fragment_cache = {}
        for pipeline in ["deskew", "binarize", "denoise"]:
            image = images[pipeline]
            fragment_cache[pipeline] = ocr_runner.easyocr_engine(image)
            fragment_cache[pipeline] += ocr_runner.tesseract_engine(image)

        # Test the combinations (ensembles) of image processing
        for pipelines in [["deskew", "binarize"], ["deskew", "binarize", "denoise"]]:
            ocr_fragments = []
            for pipeline in pipelines:
                ocr_fragments += fragment_cache[pipeline]

            # Score with consensus sequence only
            scores.append(
                builder_score(
                    args,
                    line_align,
                    gold,
                    pipelines,
                    spell_well,
                    ocr_fragments,
                    post_process=False,
                )
            )
            # Score with consensus sequence and post-processing
            scores.append(
                builder_score(
                    args,
                    line_align,
                    gold,
                    pipelines,
                    spell_well,
                    ocr_fragments,
                    post_process=True,
                )
            )

    return scores


def easy_score(args, line_align, gold, image, pipeline=""):
    """Score how EasyOCR works on an image."""
    text = ocr_runner.EngineConfig.easy_ocr.readtext(
        image, blocklist=ocr_runner.EngineConfig.char_blacklist, detail=0
    )
    text = " ".join(text)
    return new_score_rec(args, line_align, gold, pipeline, "easy", text)


def tess_score(args, line_align, gold, image, pipeline=""):
    """Score how Tesseract works on an image."""
    text = pytesseract.image_to_string(
        image, config=ocr_runner.EngineConfig.tess_config
    )
    return new_score_rec(args, line_align, gold, pipeline, "tesseract", text)


def builder_score(args, line_align, gold, pipelines, spell_well, frags, post_process):
    text = label_builder.build_label_text(frags, spell_well, line_align)
    pipeline = ",".join(pipelines)
    engines = "easy,tesseract"
    action = "label_builder" if post_process else "consensus"
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


def output_scores(args, cxn, scores):
    db.execute(cxn, "delete from ocr_scores where score_set = ?", (args.score_set,))
    df = pd.DataFrame(scores)
    df.to_sql("ocr_scores", cxn, if_exists="append", index=False)


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
