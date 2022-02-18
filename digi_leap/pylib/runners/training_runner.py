"""Run a label finder model for training, testing, or inference."""
import logging
from argparse import Namespace

import numpy as np
import torch
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from . import runner_utils as ru
from .. import db
from ..datasets.label_finder_data import LabelFinderData

# import numpy as np


def train(model, args: Namespace):
    """Train a model."""
    device = torch.device("cuda" if torch.has_cuda else "cpu")
    model.to(device)

    writer = SummaryWriter(args.log_dir)

    train_loader = get_train_loader(args)
    val_loader = get_val_loader(args)
    optimizer = get_optimizer(model, args.learning_rate)

    start_epoch = 1  # model.state.get("epoch", 0) + 1
    end_epoch = start_epoch + args.epochs

    best_loss = np.Inf  # model.state.get("best_loss", np.Inf)

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


def one_epoch(model, device, loader, optimizer=None):
    """Train or validate an epoch."""
    running_loss = 0.0

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

        running_loss += losses["loss"].item()

    return running_loss / len(loader)


def get_optimizer(model, lr):
    """Build the optimizer."""
    return torch.optim.AdamW(model.parameters(), lr=lr)


def get_train_loader(args):
    """Load the training split."""
    logging.info("Loading training data.")
    raw_data = db.select_label_split(
        args.database, split="train", label_set=args.label_set, limit=args.limit
    )
    dataset = LabelFinderData(raw_data, args.image_size, augment=True)
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        shuffle=True,
        collate_fn=ru.collate_fn,
        pin_memory=True,
    )


def get_val_loader(args):
    """Load the validation split."""
    logging.info("Loading validation data.")
    raw_data = db.select_label_split(
        args.database, split="val", label_set=args.label_set, limit=args.limit
    )
    dataset = LabelFinderData(raw_data, args.image_size, augment=False)
    return DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=ru.collate_fn,
        pin_memory=True,
    )


def save_checkpoint(model, optimizer, save_model, val_loss, best_loss, epoch):
    """Save the model if it meets criteria for being the current best model."""
    if val_loss <= best_loss:
        best_loss = val_loss
        torch.save(
            {
                "epoch": epoch,
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "best_loss": best_loss,
            },
            save_model,
        )
    return best_loss


def log_stats(writer, train_loss, val_loss, best_loss, epoch):
    """Log results of the epoch."""
    logging.info(
        f"{epoch:3}: "
        f"Train: loss {train_loss:0.6f} Valid: loss {val_loss:0.6f}"
        f"{' ++' if val_loss == best_loss else ''}"
    )
    writer.add_scalars(
        "Training vs. Validation",
        {"Training loss": train_loss, "Validation loss": val_loss},
        epoch,
    )
    writer.flush()
