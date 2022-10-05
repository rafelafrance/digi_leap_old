"""Create an expedition for checking the results of the OCR label builder."""
import os
import warnings
from argparse import Namespace

import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

from ...db import db


def build(args: Namespace) -> None:
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)
        os.makedirs(args.expedition_dir, exist_ok=True)

        texts = db.canned_select(cxn, "ocr_texts", ocr_set=args.ocr_set)

        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)
            for text in tqdm(texts):
                words = text["ocr_text"].split()
                if len(words) < args.min_words:
                    continue

                with Image.open(text["path"]) as sheet:
                    label = sheet.crop(
                        (
                            text["label_left"],
                            text["label_top"],
                            text["label_right"],
                            text["label_bottom"],
                        )
                    )

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
                        text["ocr_text"],
                        verticalalignment="top",
                        color="black",
                        fontsize=16,
                    )
                    out_path = args.expedition_dir / str(text["label_id"])
                    plt.savefig(out_path)
                    plt.close(fig)

        db.update_run_finished(cxn, run_id)
