import csv
import os
import warnings
from argparse import Namespace
from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

from ...db import db


def build_2_files(args: Namespace) -> None:
    os.makedirs(args.expedition_dir, exist_ok=True)

    csv_path = args.expedition_dir / "manifest.csv"
    with db.connect(args.database) as cxn, open(csv_path, "w") as csv_file:
        run_id = db.insert_run(cxn, args)

        writer = csv.writer(csv_file)
        writer.writerow("ocr_id image_file text_file ocr_set database".split())

        recs = db.canned_select(cxn, "ocr_texts", ocr_set=args.ocr_set)

        for rec in tqdm(recs):
            image = get_label(rec)

            image_path = Path(args.expedition_dir) / f"ocr_id_{rec['ocr_id']:04d}.jpg"
            image.save(str(image_path))

            text_path = image_path.with_suffix(".txt")
            with open(text_path, "w") as out_file:
                out_file.write(rec["ocr_text"])

            writer.writerow(
                [
                    rec["ocr_id"],
                    image_path.name,
                    text_path.name,
                    rec["ocr_set"],
                    str(args.database).replace(".", "_").replace("/", "_"),
                ]
            )

        db.update_run_finished(cxn, run_id)


def get_label(rec):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        image = Image.open(rec["path"]).convert("RGB")
        image = image.crop(
            (
                rec["label_left"],
                rec["label_top"],
                rec["label_right"],
                rec["label_bottom"],
            )
        )
    return image


def build_side_by_side(args: Namespace) -> None:
    os.makedirs(args.expedition_dir, exist_ok=True)
    csv_path = args.expedition_dir / "manifest.csv"

    with db.connect(args.database) as cxn, open(csv_path, "w") as csv_file:
        run_id = db.insert_run(cxn, args)

        writer = csv.writer(csv_file)
        writer.writerow("ocr_id image_file ocr_set database".split())

        recs = db.canned_select(cxn, "ocr_texts", ocr_set=args.ocr_set)

        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)
            for rec in tqdm(recs):
                words = rec["ocr_text"].split()

                if len(words) < args.min_words:
                    continue

                with Image.open(rec["path"]) as sheet:
                    label = sheet.crop(
                        (
                            rec["label_left"],
                            rec["label_top"],
                            rec["label_right"],
                            rec["label_bottom"],
                        )
                    )

                    text = ["\n".join(wrap(ln)) for ln in rec["ocr_text"].splitlines()]
                    text = "\n".join(text)

                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))
                    fig.set_facecolor("white")

                    ax1.axis("off")
                    ax1.set_anchor("NE")
                    ax1.imshow(label)

                    ax2.axis("off")
                    ax1.set_anchor("NW")
                    ax2.text(
                        0.0,
                        1.0,
                        text,
                        verticalalignment="top",
                        color="black",
                        fontsize=16,
                    )
                    out_path = args.expedition_dir / str(rec["label_id"])
                    plt.savefig(out_path)
                    plt.close(fig)

                    writer.writerow(
                        [
                            rec["ocr_id"],
                            out_path.name,
                            rec["ocr_set"],
                            str(args.database).replace(".", "_").replace("/", "_"),
                        ]
                    )

        db.update_run_finished(cxn, run_id)
