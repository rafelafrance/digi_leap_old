import json
import warnings
from itertools import chain
from itertools import combinations

import cppimport.import_hook  # noqa pylint: disable=unused-import
import pandas as pd
from PIL import Image
from tqdm import tqdm

from . import label_transformer
from . import ocr_runner
from .. import consts
from ..db import db
from ..label_builder import label_builder as builder
from ..label_builder.line_align import line_align_py  # noqa
from ..label_builder.line_align import line_align_subs
from ..label_builder.spell_well.spell_well import SpellWell


Actions = list[tuple[str] | tuple[str, str]]


class Scorer:
    image_processing_pipelines = ["", "deskew", "binarize", "denoise"]
    ocr_engines = ocr_runner.ENGINES

    def __init__(self, args):
        self.score_set = args.score_set
        self.gold_set = args.gold_set
        self.database = args.database

        self.combos = self._pipeline_engine_combos()
        self.line_align = line_align_py.LineAlign(line_align_subs.SUBS)
        self.spell_well = SpellWell()

    def calculate(self, gold_std):
        scores = []

        for gold in tqdm(gold_std):
            images = self._process_images(gold)
            all_frags = self._get_ocr_fragments(images, gold)

            scores += self._score_simple_ocr(gold, images)
            scores += self._score_ocr_ensembles(gold, all_frags)

        return scores

    def insert_scores(self, scores):
        df = pd.DataFrame(scores)
        with db.connect(self.database) as cxn:
            db.execute(
                cxn, "delete from ocr_scores where score_set = ?", (self.score_set,)
            )
            df.to_sql("ocr_scores", cxn, if_exists="append", index=False)

    def select_scores(self):
        with db.connect(self.database) as cxn:
            results = db.execute(
                cxn, "select * from ocr_scores where score_set = ?", (self.score_set,)
            )
            scores = [r for r in results]
        return scores

    def _get_ocr_fragments(self, images, gold):
        """Cache OCR fragments."""
        fragments = {}
        for pipeline in self.image_processing_pipelines:
            image = images[pipeline]

            results = ocr_runner.easyocr_engine(image)
            fragments[(pipeline, "easyocr")] = self._results_to_fragments(
                results, gold, pipeline, "easyocr"
            )

            results = ocr_runner.tesseract_engine(image)
            fragments[(pipeline, "tesseract")] = self._results_to_fragments(
                results, gold, pipeline, "tesseract"
            )

        return fragments

    def _score_simple_ocr(self, gold, images):
        """Score the OCR engine without an ensemble."""
        scores = []

        for pipeline, image in images.items():
            text = ocr_runner.easy_text(image)
            actions: Actions = [(pipeline, "easyocr")]
            scores.append(self._new_score_rec(gold, text, actions))

            text = builder.post_process_text(text, self.spell_well)
            actions: Actions = [(pipeline, "easyocr"), ("post_process",)]
            scores.append(self._new_score_rec(gold, text, actions))

            text = ocr_runner.tess_text(image)
            actions: Actions = [(pipeline, "tesseract")]
            scores.append(self._new_score_rec(gold, text, actions))

            text = builder.post_process_text(text, self.spell_well)
            actions: Actions = [(pipeline, "tesseract"), ("post_process",)]
            scores.append(self._new_score_rec(gold, text, actions))

        return scores

    def _score_ocr_ensembles(self, gold, all_frags):
        scores = []

        for combo in self.combos:
            frags = [all_frags[t] for t in combo]
            frags = list(chain(*frags))

            text = builder.build_label_text(frags, self.spell_well, self.line_align)
            scores.append(self._new_score_rec(gold, text, combo))

            text = builder.post_process_text(text, self.spell_well)
            actions = combo + [("post_process",)]
            scores.append(self._new_score_rec(gold, text, actions))

        return scores

    def _new_score_rec(self, gold, text, actions):
        gold_text = " ".join(gold["gold_text"].split())
        text = " ".join(text.split())
        actions = [list(a) for a in actions]
        return {
            "gold_id": gold["gold_id"],
            "gold_set": self.gold_set,
            "label_id": gold["label_id"],
            "score_set": self.score_set,
            "actions": json.dumps(actions),
            "score_text": text,
            "score": self.line_align.levenshtein(gold_text, text),
        }

    @staticmethod
    def _results_to_fragments(results, gold, pipeline, engine):
        fragments = []
        for result in results:
            fragments.append(
                result
                | {
                    "label_id": gold["label_id"],
                    "ocr_set": gold["gold_set"],
                    "engine": engine,
                    "pipeline": pipeline,
                }
            )
        return fragments

    def _process_images(self, gold):
        images = {}
        for pipeline in self.image_processing_pipelines:
            images[pipeline] = self._get_label_image(gold, pipeline)
        return images

    @staticmethod
    def _get_label_image(gold, pipeline=""):
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

    def _pipeline_engine_combos(self) -> list[Actions]:
        pipes = self._image_processing_combos()
        engines = self._ocr_engine_combos()

        combos = []
        for pipe in pipes:
            for engine in engines:
                combos.append([(p, e) for p in pipe for e in engine])

        return [c for c in combos if len(c) > 1]

    def _ocr_engine_combos(self) -> list[list[str]]:
        engines = []
        for r in range(1, len(self.ocr_engines) + 1):
            engines += [list(c) for c in combinations(self.ocr_engines, r)]
        return engines

    def _image_processing_combos(self) -> list[list[str]]:
        pipes = []
        for r in range(1, len(self.image_processing_pipelines) + 1):
            pipes += [list(c) for c in combinations(self.image_processing_pipelines, r)]
        return pipes


# ##################################################################################
def select_gold_std(database, gold_set):
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


def insert_gold_std(csv_path, database, gold_set):
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
