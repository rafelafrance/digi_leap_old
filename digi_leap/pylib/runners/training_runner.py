"""Run a label finder model for training, testing, or inference."""
import logging
from abc import ABC
from abc import abstractmethod
from argparse import Namespace

import numpy as np
import torch
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from digi_leap.pylib import db
from digi_leap.pylib.datasets.label_finder_data import LabelFinderData

ArgsType = Namespace


class LabelFinderRunner(ABC):
    """Base class for running a label finder model."""

    def __init__(self, model, args: ArgsType):
        self.model = model

        self.batch_size = args.batch_size
        self.database = args.database
        self.workers = args.workers
        self.limit = args.limit

        self.device = torch.device("cuda" if torch.has_cuda else "cpu")
        self.model.to(self.device)

    @abstractmethod
    def run(self):
        """Perform the main function of the class."""


class LabelFinderTrainingRunner(LabelFinderRunner):
    """Train a label finder model."""

    def __init__(self, model, args: ArgsType):
        super().__init__(model, args)

        self.lr = args.learning_rate
        self.save_model = args.save_model
        self.label_set = args.label_set

        self.writer = SummaryWriter(args.log_dir)

        self.train_loader = self.train_dataloader()
        self.val_loader = self.val_dataloader()
        self.optimizer = self.configure_optimizers()
        # self.criterion = self.configure_criterion(self.train_loader.dataset)

        self.best_loss = self.model.state.get("best_loss", np.Inf)
        self.best_acc = self.model.state.get("accuracy", 0.0)
        self.run_loss = np.Inf
        self.run_acc = 0.0

        self.start_epoch = self.model.state.get("epoch", 0) + 1
        self.end_epoch = self.start_epoch + args.epochs

    def run(self):
        """Train the model."""
        logging.info("Training started.")

        for epoch in range(self.start_epoch, self.end_epoch):
            self.model.train()

        self.writer.close()

    def configure_optimizers(self):
        """."""
        return torch.optim.AdamW(self.model.parameters(), lr=self.lr)

    def train_dataloader(self):
        """Load the training split."""
        logging.info("Loading training data.")
        raw_data = db.select_label_split(
            self.database, split="train", label_set=self.label_set, limit=self.limit
        )
        dataset = LabelFinderData(raw_data, augment=True)
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            num_workers=self.workers,
            shuffle=True,
            pin_memory=True,
        )

    def val_dataloader(self):
        """Load the validation split."""
        logging.info("Loading validation data.")
        raw_data = db.select_label_split(
            self.database, split="val", label_set=self.label_set, limit=self.limit
        )
        dataset = LabelFinderData(raw_data, augment=True)
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            num_workers=self.workers,
            pin_memory=True,
        )
