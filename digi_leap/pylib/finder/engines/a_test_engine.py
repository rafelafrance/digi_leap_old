import logging
from argparse import Namespace
from dataclasses import dataclass

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from . import engine_utils
from ... import consts
from ...db import db
from ..datasets.labeled_data import LabeledData
from ..models import model_utils


@dataclass
class Stats:
    total_loss: float = float("Inf")
    class_loss: float = float("Inf")
    box_loss: float = float("Inf")


def evaluate(model, args: Namespace):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        device = torch.device("cuda" if torch.has_cuda else "cpu")

        model_utils.load_model_state(model, args.load_model)
        model.to(device)

        eval_loader = get_data_loader(cxn, args)

        logging.info("Evaluation started.")

        model.eval()
        batch, stats = run_evaluator(model, device, eval_loader)

        insert_evaluation_records(cxn, batch, args.test_set, args.image_size)

        log_stats(stats, cxn, run_id)


def run_evaluator(model, device, loader):
    batch = []

    running_loss = Stats(
        total_loss=0.0,
        class_loss=0.0,
        box_loss=0.0,
    )

    for images, annotations, sheet_ids in tqdm(loader):
        images = images.to(device)

        annotations["bbox"] = [b.to(device) for b in annotations["bbox"]]
        annotations["cls"] = [c.to(device) for c in annotations["cls"]]
        annotations["img_size"] = annotations["img_size"].to(device)
        annotations["img_scale"] = annotations["img_scale"].to(device)

        losses = model(images, annotations)

        for detections, sheet_id in zip(losses["detections"], sheet_ids):
            for left, top, right, bottom, conf, pred_class in detections:
                batch.append(
                    {
                        "sheet_id": sheet_id.item(),
                        "pred_class": int(pred_class.item()),
                        "pred_conf": conf.item(),
                        "pred_left": int(left.item()),
                        "pred_top": int(top.item()),
                        "pred_right": int(right.item()),
                        "pred_bottom": int(bottom.item()),
                    }
                )

        running_loss.total_loss += losses["loss"].item()
        running_loss.class_loss += losses["class_loss"].item()
        running_loss.box_loss += losses["box_loss"].item()

    return batch, Stats(
        total_loss=running_loss.total_loss / len(loader),
        class_loss=running_loss.class_loss / len(loader),
        box_loss=running_loss.box_loss / len(loader),
    )


def insert_evaluation_records(cxn, batch, test_set, image_size):
    rows = db.execute(cxn, "select * from sheets where split = 'test'")

    sheets: dict[str, tuple] = {}

    for row in rows:
        wide = row["width"] / image_size
        high = row["height"] / image_size
        sheets[row["sheet_id"]] = (wide, high)

    for row in batch:
        row["test_set"] = test_set
        row["pred_class"] = consts.CLASS2NAME[row["pred_class"]]

        wide, high = sheets[row["sheet_id"]]

        row["pred_left"] = int(row["pred_left"] * wide)
        row["pred_right"] = int(row["pred_right"] * wide)

        row["pred_top"] = int(row["pred_top"] * high)
        row["pred_bottom"] = int(row["pred_bottom"] * high)

    db.execute(cxn, "delete from label_finder_tests where test_set = ?", (test_set,))
    db.canned_insert(cxn, "label_finder_tests", batch)


def get_data_loader(cxn, args):
    logging.info("Loading eval data.")
    raw_data = db.canned_select(
        cxn, "train_split", split="test", train_set=args.train_set
    )
    dataset = LabeledData(raw_data, args.image_size, augment=False)
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=engine_utils.collate_fn,
        pin_memory=True,
    )


def log_stats(stats, cxn, run_id):
    comments = (
        f"Eval: total loss {stats.total_loss:0.6f}  "
        f"class loss {stats.class_loss:0.6f}  "
        f"box loss {stats.box_loss:0.6f}"
    )
    logging.info(comments)
    db.update_run_comments(cxn, run_id, comments)
