"""Run a label finder model for training, testing, or inference."""
import logging
from argparse import Namespace
from dataclasses import dataclass

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from . import runner_utils
from ... import consts
from ... import db
from ..datasets.labeled_data import LabeledData
from ..models import model_utils


@dataclass
class Stats:

    total_loss: float = float("Inf")
    class_loss: float = float("Inf")
    box_loss: float = float("Inf")


def test(model, args: Namespace):
    run_id = db.insert_run(args)

    device = torch.device("cuda" if torch.has_cuda else "cpu")

    model_utils.load_model_state(model, args.load_model)
    model.to(device)

    test_loader = get_data_loader(args)

    logging.info("Testing started.")

    model.eval()
    batch, stats = run_test(model, device, test_loader)

    insert_test_records(args.database, batch, args.test_set, args.image_size)

    log_stats(stats, args.database, run_id)


def run_test(model, device, loader):
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


def insert_test_records(database, batch, test_set, image_size):
    db.create_tests_table(database)

    rows = db.rows_as_dicts(database, "select * from sheets where split = 'test'")

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

    db.delete(database, "tests", test_set=test_set)
    db.insert_tests(database, batch)


def get_data_loader(args):
    logging.info("Loading test data.")
    raw_data = db.select_label_split(
        args.database, split="test", label_set=args.label_set, limit=args.limit
    )
    dataset = LabeledData(raw_data, args.image_size, augment=False)
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=runner_utils.collate_fn,
        pin_memory=True,
    )


def log_stats(stats, database, run_id):
    comments = (
        f"Test: total loss {stats.total_loss:0.6f}  "
        f"class loss {stats.class_loss:0.6f}  "
        f"box loss {stats.box_loss:0.6f}"
    )
    logging.info(comments)
    db.update_run_comments(database, run_id, comments)
