"""Run a label finder model for training, testing, or inference."""
import logging
from argparse import Namespace

import torch.multiprocessing
from torch.utils.data import DataLoader
from tqdm import tqdm

from . import runner_utils
from ... import consts
from ... import db
from ..datasets.unlabeled_data import UnlabeledData
from ..models import model_utils


def predict(model, args: Namespace):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        torch.multiprocessing.set_sharing_strategy("file_system")

        device = torch.device("cuda" if torch.has_cuda else "cpu")

        model_utils.load_model_state(model, args.load_model)
        model.to(device)

        test_loader = get_data_loader(cxn, args)

        logging.info("Testing started.")

        model.eval()
        batch = run_prediction(model, device, test_loader)

        insert_label_records(cxn, batch, args.label_set, args.image_size)

        db.update_run_finished(cxn, run_id)


def run_prediction(model, device, loader):
    batch = []

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
                        "class": int(pred_class.item()),
                        "label_conf": conf.item(),
                        "label_left": int(left.item()),
                        "label_top": int(top.item()),
                        "label_right": int(right.item()),
                        "label_bottom": int(bottom.item()),
                    }
                )

    return batch


def insert_label_records(cxn, batch, label_set, image_size):
    db.create_tests_table(cxn)

    rows = db.execute(cxn, "select * from sheets")
    sheets: dict[str, tuple] = {}

    for row in rows:
        wide = row["width"] / image_size
        high = row["height"] / image_size
        sheets[row["sheet_id"]] = (wide, high)

    prev_sheet_id = ""
    offset = 0

    for row in batch:
        row["label_set"] = label_set
        row["class"] = consts.CLASS2NAME[row["class"]]

        wide, high = sheets[row["sheet_id"]]

        row["label_left"] = int(row["label_left"] * wide)
        row["label_right"] = int(row["label_right"] * wide)

        row["label_top"] = int(row["label_top"] * high)
        row["label_bottom"] = int(row["label_bottom"] * high)

        offset = offset + 1 if row["sheet_id"] == prev_sheet_id else 0
        row["offset"] = offset

        prev_sheet_id = row["sheet_id"]

    db.execute(cxn, "delete from labels where label_set = ?", (label_set,))
    db.insert_labels(cxn, batch)


def get_data_loader(cxn, args):
    logging.info("Loading image data.")
    raw_data = db.execute(cxn, "select * from sheets")
    dataset = UnlabeledData(raw_data, args.image_size)
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=runner_utils.collate_fn,
        pin_memory=True,
    )
