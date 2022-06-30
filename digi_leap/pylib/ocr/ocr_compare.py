import warnings
from itertools import combinations

import cppimport.import_hook  # noqa pylint: disable=unused-import
import pandas as pd
from PIL import Image

from . import label_transformer
from . import ocr_runner
from .. import consts
from ..db import db
from ..label_builder import label_builder as builder
from ..label_builder.line_align import line_align_py  # noqa
from ..label_builder.line_align import line_align_subs
from ..label_builder.spell_well.spell_well import SpellWell


PIPELINES = ["", "deskew", "binarize", "denoise"]

LINE_ALIGN = None
SPELL_WELL = None


def line_align():
    """Cache the line_align object."""
    global LINE_ALIGN
    if not LINE_ALIGN:
        LINE_ALIGN = line_align_py.LineAlign(line_align_subs.SUBS)
    return LINE_ALIGN


def spell_well():
    """Cache the SpellWell object."""
    global SPELL_WELL
    if not SPELL_WELL:
        SPELL_WELL = SpellWell()
    return SPELL_WELL


def get_gold_std(database, gold_set):
    sql = """
        select *
        from gold_standard
        join labels using (label_id)
        join sheets using (sheet_id)
        where gold_set = ?
        """
    with db.connect(database) as cxn:
        gold = cxn.execute(sql, (gold_set,))
    return [dict(r) for r in gold]


def new_gold_std(csv_path, database, gold_set):
    df = pd.read_csv(csv_path).fillna("")
    df = df.loc[df.text != ""]

    df["label_id"] = df["label"].str.split("_").str[2]
    df["label_id"] = df["label_id"].str.split(".").str[0].astype(int)

    df["sheet_id"] = df["label"].str.split("_").str[1]

    df["gold_set"] = gold_set

    df = df.drop(["sheet", "label"], axis="columns")
    df = df.rename(columns={"text": "gold_text"})

    with db.connect(database) as cxn:
        df.to_sql("gold_standard", cxn, if_exists="append", index=False)


def pipeline_engine_combos():
    pipes = []
    for r in range(1, len(PIPELINES) + 1):
        pipes += combinations(PIPELINES, r)

    engines = []
    for r in range(1, len(ocr_runner.ENGINES) + 1):
        engines += combinations(ocr_runner.ENGINES, r)

    combos = []
    for pipe in pipes:
        for engine in engines:
            combos.append([(p, e) for p in pipe for e in engine])

    return [c for c in combos if len(c) > 1]


def get_ocr_fragments(images, gold):
    fragments = {}
    for pipeline in PIPELINES:
        image = images[pipeline]

        results = ocr_runner.easyocr_engine(image)
        fragments[(pipeline, "easyocr")] = []
        for result in results:
            fragments[(pipeline, "easyocr")].append(
                result
                | {
                    "label_id": gold["label_id"],
                    "ocr_set": gold["gold_set"],
                    "engine": "easyocr",
                    "pipeline": pipeline,
                }
            )

        results = ocr_runner.tesseract_engine(image)
        fragments[(pipeline, "tesseract")] = []
        for result in results:
            fragments[(pipeline, "tesseract")].append(
                result
                | {
                    "label_id": gold["label_id"],
                    "ocr_set": gold["gold_set"],
                    "engine": "tesseract",
                    "pipeline": pipeline,
                }
            )

    return fragments


def process_images(gold):
    images = {}
    for pipeline in PIPELINES:
        image = read_label(gold, pipeline)
        images[pipeline] = image
    return images


def simple_ocr(args, gold, images):
    scores = []
    for pipeline, image in images.items():
        text = ocr_runner.easy_text(image)
        actions = str((pipeline, "easyocr"))
        scores.append(new_score_rec(args, gold, text, actions))

        text = builder.post_process_text(text, spell_well())
        actions = str((pipeline, "easyocr")) + " post_process"
        scores.append(new_score_rec(args, gold, text, actions))

        text = ocr_runner.tess_text(image)
        actions = str((pipeline, "tesseract"))
        scores.append(new_score_rec(args, gold, text, actions))

        text = builder.post_process_text(text, spell_well())
        actions = str((pipeline, "tesseract")) + " post_process"
        scores.append(new_score_rec(args, gold, text, actions))

    return scores


def new_score_rec(args, gold, text, actions):
    gold_text = " ".join(gold["gold_text"].split())
    text = " ".join(text.split())
    return {
        "gold_id": gold["gold_id"],
        "gold_set": args.gold_set,
        "label_id": gold["label_id"],
        "score_set": args.score_set,
        "actions": actions,
        "score_text": text,
        "levenshtein": line_align().levenshtein(gold_text, text),
    }


def read_label(gold, pipeline=""):
    with warnings.catch_warnings():  # Turn off EXIF warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        path = consts.ROOT_DIR / gold["path"]
        sheet = Image.open(path)
        label = sheet.crop(
            (
                gold["label_left"],
                gold["label_top"],
                gold["label_right"],
                gold["label_bottom"],
            )
        )

    if pipeline:
        label = label_transformer.transform_label(pipeline, label)

    return label


def output_scores(args, cxn, scores):
    db.execute(cxn, "delete from ocr_scores where score_set = ?", (args.score_set,))
    df = pd.DataFrame(scores)
    df.to_sql("ocr_scores", cxn, if_exists="append", index=False)
