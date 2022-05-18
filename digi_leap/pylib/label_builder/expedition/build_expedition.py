import warnings
from argparse import Namespace
from os import makedirs

import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

from ...db import db


def build(args: Namespace) -> None:
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)
        makedirs(args.expedition_dir, exist_ok=True)

        cons = db.canned_select("sample_cons", cxn, consensus_set=args.consensus_set)

        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)
            for consensus in tqdm(cons):
                words = consensus["consensus_text"].split()
                if len(words) < args.min_words:
                    continue

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
                        consensus["consensus_text"],
                        verticalalignment="top",
                        color="black",
                        fontsize=16,
                    )
                    out_path = args.expedition_dir / str(consensus["label_id"])
                    plt.savefig(out_path)
                    plt.close(fig)

        db.update_run_finished(cxn, run_id)
