import csv
import os
import warnings
from argparse import Namespace
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from ...db import db
from ..ocr_labels import Ensemble


def build(args: Namespace) -> None:
    os.makedirs(args.expedition_dir, exist_ok=True)

    sql = """
        select *
        from   gold_standard
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  gold_set = ?
        """

    csv_path = args.expedition_dir / "manifest.csv"
    with db.connect(args.database) as cxn, open(csv_path, "w") as csv_file:
        run_id = db.insert_run(cxn, args)

        ensemble = Ensemble(args)

        writer = csv.writer(csv_file)
        writer.writerow("gold_id image_file text_file pipeline database".split())

        golden = db.execute(cxn, sql, [args.gold_set])

        for gold in tqdm(golden):
            image = get_golden_label(gold)
            text = ensemble.run(image)

            image_path = (
                Path(args.expedition_dir) / f"gold_id_{gold['gold_id']:04d}.jpg"
            )
            image.save(str(image_path))

            text_path = image_path.with_suffix(".txt")
            with open(text_path, "w") as out_file:
                out_file.write(text)

            writer.writerow(
                [
                    gold["gold_id"],
                    image_path.name,
                    text_path.name,
                    ensemble.pipeline,
                    str(args.database).replace(".", "_").replace("/", "_"),
                ]
            )

        db.update_run_finished(cxn, run_id)


def get_golden_label(gold):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        image = Image.open(gold["path"]).convert("RGB")
        image = image.crop(
            (
                gold["label_left"],
                gold["label_top"],
                gold["label_right"],
                gold["label_bottom"],
            )
        )
    return image
