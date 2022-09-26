import logging
from argparse import Namespace

import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from ... import consts
from ...db import db
from ..datasets.labeled_data_fasterrcnn import LabeledData
from ..models import model_utils


def evaluate(model, args: Namespace):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        device = torch.device("cuda" if torch.has_cuda else "cpu")

        model_utils.load_model_state(model, args.load_model)
        model.to(device)

        test_loader = get_test_loader(cxn, args)

        logging.info("Evaluation started.")

        model.eval()
        batch = run_evaluator(model, test_loader, device)

        insert_evaluation_records(
            cxn, batch, args.train_set, args.test_set, args.image_size
        )

        db.update_run_finished(cxn, run_id)


def run_evaluator(model, loader, device):
    batch = []

    for images, targets, *_ in tqdm(loader):
        images = list(image.to(device) for image in images)
        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

        with torch.no_grad():
            preds = model(images, targets)

        for target, pred in zip(targets, preds):
            for box, label, score in zip(pred["boxes"], pred["labels"], pred["scores"]):
                left, top, right, bottom = box
                batch.append(
                    {
                        "sheet_id": target["image_id"].item(),
                        "test_class": int(label.item()),
                        "test_conf": score.item(),
                        "test_left": int(left.item()),
                        "test_top": int(top.item()),
                        "test_right": int(right.item()),
                        "test_bottom": int(bottom.item()),
                    }
                )

    return batch


def insert_evaluation_records(cxn, batch, train_set, test_set, image_size):
    rows = db.canned_select(cxn, "label_train_split", train_set=train_set, split="test")

    sheets: dict[str, tuple] = {}

    for row in rows:
        wide = row["width"] / image_size
        high = row["height"] / image_size
        sheets[row["sheet_id"]] = (wide, high)

    for row in batch:
        row["test_set"] = test_set
        row["train_set"] = train_set
        row["test_class"] = consts.CLASS2NAME[row["test_class"]]

        wide, high = sheets[row["sheet_id"]]

        row["test_left"] = int(row["test_left"] * wide)
        row["test_right"] = int(row["test_right"] * wide)

        row["test_top"] = int(row["test_top"] * high)
        row["test_bottom"] = int(row["test_bottom"] * high)

    db.canned_delete(cxn, "label_tests", test_set=test_set)
    db.canned_insert(cxn, "label_tests", batch)


def get_test_loader(cxn, args):
    logging.info("Loading training data.")
    raw_data = db.canned_select(
        cxn, "label_train_split", split="test", train_set=args.train_set
    )
    dataset = LabeledData(raw_data, args.image_size, augment=False)
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=LabeledData.collate_fn,
        pin_memory=True,
    )
