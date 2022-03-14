"""Build an expedition for scoring consensus text output."""
import warnings
from argparse import Namespace
from os import makedirs

import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

from ... import db


def build(args: Namespace) -> None:
    """Build the expedition."""
    run_id = db.insert_run(args)

    makedirs(args.expedition_dir, exist_ok=True)

    cons = db.sample_consensus(args.database, args.cons_set, limit=args.limit)

    count = 0

    with warnings.catch_warnings():  # Turn off EXIF warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        for consensus in tqdm(cons):
            words = consensus["cons_text"].split()
            if len(words) < args.min_words:
                continue

            count += 1
            if count > args.limit:
                break

            with Image.open(consensus["path"]) as sheet:
                label = sheet.crop(
                    (
                        consensus["label_left"],
                        consensus["label_top"],
                        consensus["label_right"],
                        consensus["label_bottom"],
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
                    consensus["cons_text"],
                    verticalalignment="top",
                    color="black",
                    fontsize=16,
                )
                out_path = args.expedition_dir / str(consensus["label_id"])
                plt.savefig(out_path)
                plt.close(fig)

    db.update_run_finished(args.database, run_id)
