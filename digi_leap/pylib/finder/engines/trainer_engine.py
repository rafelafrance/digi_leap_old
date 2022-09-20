import logging
from argparse import Namespace
from dataclasses import dataclass

import torch
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from . import engine_utils
from ...db import db
from ..datasets.labeled_data import LabeledData
from ..models import model_utils


@dataclass
class Stats:
    total_loss: float = float("Inf")
    class_loss: float = float("Inf")
    box_loss: float = float("Inf")


def train(model, args: Namespace):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        device = torch.device("cuda" if torch.has_cuda else "cpu")

        model_utils.load_model_state(model, args.load_model)
        model.to(device)

        writer = SummaryWriter(args.log_dir)

        train_loader = get_train_loader(cxn, args)
        val_loader = get_val_loader(cxn, args)
        optimizer = get_optimizer(model, args.learning_rate)

        start_epoch = 1  # model.state.get("epoch", 0) + 1
        end_epoch = start_epoch + args.epochs

        best_loss = Stats()

        logging.info("Training started.")

        for epoch in range(start_epoch, end_epoch):
            model.train()
            train_loss = one_epoch(model, device, train_loader, optimizer)

            model.eval()
            val_loss = one_epoch(model, device, val_loader)

            best_loss = save_checkpoint(
                model, optimizer, args.save_model, val_loss, best_loss, epoch
            )
            log_stats(writer, train_loss, val_loss, best_loss, epoch)

        writer.close()
        db.update_run_comments(cxn, run_id, comments(best_loss))


def one_epoch(model, device, loader, optimizer=None):
    running_loss = Stats(
        total_loss=0.0,
        class_loss=0.0,
        box_loss=0.0,
    )

    for images, annotations, *_ in loader:
        images = images.to(device)

        annotations["bbox"] = [b.to(device) for b in annotations["bbox"]]
        annotations["cls"] = [c.to(device) for c in annotations["cls"]]
        annotations["img_size"] = annotations["img_size"].to(device)
        annotations["img_scale"] = annotations["img_scale"].to(device)

        losses = model(images, annotations)

        if optimizer:
            optimizer.zero_grad()
            losses["loss"].backward()
            optimizer.step()

        running_loss.total_loss += losses["loss"].item()
        running_loss.class_loss += losses["class_loss"].item()
        running_loss.box_loss += losses["box_loss"].item()

    return Stats(
        total_loss=running_loss.total_loss / len(loader),
        class_loss=running_loss.class_loss / len(loader),
        box_loss=running_loss.box_loss / len(loader),
    )


def get_optimizer(model, lr):
    return torch.optim.AdamW(model.parameters(), lr=lr)


def get_train_loader(cxn, args):
    logging.info("Loading training data.")
    raw_data = db.canned_select(
        cxn, "train_split", split="train", train_set=args.train_set
    )
    dataset = LabeledData(raw_data, args.image_size, augment=True, limit=args.limit)
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        shuffle=True,
        collate_fn=engine_utils.collate_fn,
        pin_memory=True,
    )


def get_val_loader(cxn, args):
    logging.info("Loading validation data.")
    raw_data = db.canned_select(
        cxn, "train_split", split="val", train_set=args.train_set
    )
    dataset = LabeledData(raw_data, args.image_size, augment=False, limit=args.limit)
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=engine_utils.collate_fn,
        pin_memory=True,
    )


def save_checkpoint(model, optimizer, save_model, val_loss, best_loss, epoch):
    if val_loss.total_loss <= best_loss.total_loss:
        best_loss = val_loss
        torch.save(
            {
                "epoch": epoch,
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "total_loss": best_loss.total_loss,
                "class_loss": best_loss.class_loss,
                "box_loss": best_loss.box_loss,
            },
            save_model,
        )
    return best_loss


def log_stats(writer, train_loss, val_loss, best_loss, epoch):
    logging.info(
        (
            "%3d "
            "Train: box loss %0.6f class loss %0.6f total loss %0.6f "
            "Validation: box loss %0.6f class loss %0.6f total loss %0.6f "
            "%s"
        ),
        epoch,
        train_loss.box_loss,
        train_loss.class_loss,
        train_loss.total_loss,
        val_loss.box_loss,
        val_loss.class_loss,
        val_loss.total_loss,
        "++" if val_loss.total_loss == best_loss.total_loss else "",
    )
    writer.add_scalars(
        "Training vs. Validation",
        {
            "Training total loss": train_loss.total_loss,
            "Training class loss": train_loss.class_loss,
            "Training box loss": train_loss.box_loss,
            "Validation total loss": val_loss.total_loss,
            "Validation class loss": val_loss.class_loss,
            "Validation box loss": val_loss.box_loss,
        },
        epoch,
    )
    writer.flush()


def comments(best_loss):
    return (
        f"Best validation: total loss {best_loss.total_loss:0.6f} "
        f"box loss: {best_loss.box_loss:0.6f} class loss: {best_loss.class_loss:0.6f}"
    )
