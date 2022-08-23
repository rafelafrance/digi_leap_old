import json
import warnings
from itertools import combinations

import cppimport.import_hook  # noqa pylint: disable=unused-import
import pandas as pd
from PIL import Image
from tqdm import tqdm

from . import label_transformer
from . import ocr_runner
from .. import consts
from ..db import db
from ..label_builder import label_builder
from ..label_builder import ocr_results
from ..label_builder.line_align import char_sub_matrix as subs
from ..label_builder.line_align import line_align_py  # noqa
from ..label_builder.spell_well.spell_well import SpellWell

IMAGE_TRANSFORMS = ["", "deskew", "binarize", "denoise"]


class Golden:
    def __init__(self, gold_rec):
        self.path = gold_rec["path"]

        self.label_id = gold_rec["label_id"]
        self.gold_id = gold_rec["gold_id"]

        self.label_left = gold_rec["label_left"]
        self.label_top = gold_rec["label_top"]
        self.label_right = gold_rec["label_right"]
        self.label_bottom = gold_rec["label_bottom"]

        self.gold_text = " ".join(gold_rec["gold_text"].split())

        self.pipe_text: dict[tuple[str, str], str] = {}


class Scorer:
    def __init__(self, gold_set, score_set, char_set="default"):
        self.gold_set = gold_set
        self.score_set = score_set
        matrix = subs.select_char_sub_matrix(char_set=char_set)
        self.line_align = line_align_py.LineAlign(matrix)
        self.spell_well = SpellWell()

    def ocr(self, gold_std) -> list[Golden]:
        golden = []
        for gold in tqdm(gold_std, desc="ocr"):
            gold = Golden(gold_rec=gold)
            original = self.get_label(gold)
            for transform in IMAGE_TRANSFORMS:
                image = self.transform_image(original, transform)
                gold.pipe_text[(transform, "easyocr")] = ocr_runner.easy_text(image)
                gold.pipe_text[(transform, "tesseract")] = ocr_runner.tess_text(image)
            golden.append(gold)
        return golden

    def score(self, golden: list[Golden]) -> list[dict]:
        scores = []
        pipelines = self.get_pipelines(golden[0])

        for gold in tqdm(golden, desc="score"):
            for pipeline in pipelines:
                lines = [gold.pipe_text[p] for p in pipeline]
                lines = ocr_results.sort_lines(lines, self.line_align)

                aligned = self.line_align.align(lines)

                # Pipeline without post-processing
                text = ocr_results.consensus(aligned, self.spell_well)
                text = text.replace("⋄", "")  # Remove gaps
                scores.append(self.score_rec(gold, text, pipeline))

                # Pipeline with post-processing
                text = label_builder.post_process_text(text, self.spell_well)
                pipeline.append(("post_process",))
                scores.append(self.score_rec(gold, text, pipeline))

        return scores

    def insert_scores(self, scores, database):
        with db.connect(database) as cxn:
            db.execute(
                cxn, "delete from ocr_scores where score_set = ?", (self.score_set,)
            )
            db.canned_insert("ocr_scores", cxn, scores)

    def select_scores(self, database):
        with db.connect(database) as cxn:
            results = db.execute(
                cxn, "select * from ocr_scores where score_set = ?", (self.score_set,)
            )
            scores = [dict(r) for r in results]
        return scores

    def score_rec(self, gold, text, pipeline):
        actions = [list(a) for a in pipeline]
        return {
            "score_set": self.score_set,
            "label_id": gold.label_id,
            "gold_id": gold.gold_id,
            "gold_set": self.gold_set,
            "actions": json.dumps(actions),
            "score_text": text,
            "score": self.line_align.levenshtein(gold.gold_text, text),
        }

    @staticmethod
    def get_pipelines(gold) -> list[list[tuple[str, str] | tuple[str]]]:
        pipelines = []
        keys = sorted(gold.pipe_text.keys())
        for r in range(1, len(keys) + 1):
            pipelines += [list(c) for c in combinations(keys, r)]
        return pipelines

    @staticmethod
    def get_label(gold: Golden):
        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)
            path = consts.ROOT_DIR / gold.path
            sheet = Image.open(path)
            label = sheet.crop(
                (
                    gold.label_left,
                    gold.label_top,
                    gold.label_right,
                    gold.label_bottom,
                )
            )
        return label

    @staticmethod
    def transform_image(image, transform):
        if not transform:
            return image
        return label_transformer.transform_label(transform, image)


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
    df = df.loc[df.gold_text != ""]

    df["label_id"] = df["label"].str.split("_").str[2]
    df["label_id"] = df["label_id"].str.split(".").str[0].astype(int)

    df["sheet_id"] = df["label"].str.split("_").str[1]

    df["gold_set"] = gold_set

    df = df.drop(["sheet", "label"], axis="columns")

    with db.connect(database) as cxn:
        df.to_sql("gold_standard", cxn, if_exists="append", index=False)
