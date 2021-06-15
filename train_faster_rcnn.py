#!/usr/bin/env python3
"""Train a model to recognize digits on allometry sheets."""

import argparse
import textwrap
from os import makedirs
from pathlib import Path
from random import randint

import numpy as np
import torch
import torch.optim as optim
import torchvision
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

from digi_leap.detection.engine import evaluate, train_one_epoch
from digi_leap.faster_rcnn_data import FasterRcnnData
from digi_leap.log import finished, started
from digi_leap.subject import TYPE_CLASSES
import digi_leap.detection.utils as utils


def train(args):
    """Train the neural net."""
    make_dirs(args)

    model = get_model()
    epoch_start = continue_training(args.model_dir, args.trained_model, model)
    epoch_end = epoch_start + args.epochs

    device = torch.device(args.device)
    model.to(device)

    train_loader, score_loader = get_loaders(args)

    # optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(
        params, lr=0.005, momentum=0.9, weight_decay=0.0005)

    lr_scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, step_size=3, gamma=0.1)

    for epoch in range(epoch_start, epoch_end):
        np.random.seed(args.seed + epoch)

        train_one_epoch(model, optimizer, train_loader, device, epoch, print_freq=100)
        lr_scheduler.step()
        evaluate(model, score_loader, device=device)


def get_loaders(args):
    """Get the data loaders."""
    subjects = FasterRcnnData.read_subjects(args.csv_file, args.image_dir)
    train_subjects, score_subjects = train_test_split(
        subjects, test_size=args.split, random_state=args.seed)
    train_dataset = FasterRcnnData(train_subjects, True)
    score_dataset = FasterRcnnData(score_subjects, False)

    train_loader = DataLoader(
        train_dataset,
        shuffle=True,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=utils.collate_fn,
        worker_init_fn=lambda w: np.random.seed(np.random.get_state()[1][0] + w),
    )

    score_loader = DataLoader(
        score_dataset,
        batch_size=args.batch_size,
        num_workers=args.workers,
        collate_fn=utils.collate_fn,
        worker_init_fn=lambda w: np.random.seed(np.random.get_state()[1][0] + w),
    )

    return train_loader, score_loader


def make_dirs(args):
    """Create output directories."""
    if args.model_dir:
        makedirs(args.model_dir, exist_ok=True)


def continue_training(model_dir, trained_model, model):
    """Continue training the model."""
    if trained_model:
        return load_model_state(model_dir / trained_model, model)
    return 1


def load_model_state(trained_model, model):
    """Load a saved model."""
    start = 1
    if trained_model:
        state = torch.load(trained_model)
        model.load_state_dict(state)
        if model.state_dict().get('epoch'):
            start = model.state_dict()['epoch'] + 1
    return start


def get_model():
    """Get the model to use."""
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(
        in_features, len(TYPE_CLASSES))
    return model


def parse_args():
    """Process command-line arguments."""
    description = """Train a model to find labels on herbarium sheets."""
    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        fromfile_prefix_chars='@')

    arg_parser.add_argument(
        '--csv-file', required=True, type=Path,
        help="""The CSV file containing reconciled data.""")

    arg_parser.add_argument(
        '--image-dir', required=True, type=Path,
        help="""Read training images from this directory.""")

    arg_parser.add_argument(
        '--split', type=float, default=0.25,
        help="""Fraction of subjects in the score dataset. (default: %(default)s)""")

    arg_parser.add_argument(
        '--model-dir', type=Path, help="""Save models to this directory.""")

    arg_parser.add_argument(
        '--trained-model',
        help="""Load this model state to continue training the model. The file must
            be in the --model-dir.""")

    arg_parser.add_argument(
        '--suffix',
        help="""Add this to the saved model name to differentiate it from
            other runs.""")

    default = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    arg_parser.add_argument(
        '--device', default=default,
        help="""Which GPU or CPU to use. Options are 'cpu', 'cuda:0', 'cuda:1' etc.
            (default: %(default)s)""")

    arg_parser.add_argument(
        '--epochs', type=int, default=100,
        help="""How many epochs to train. (default: %(default)s)""")

    arg_parser.add_argument(
        '--learning-rate', type=float, default=0.0001,
        help="""Initial learning rate. (default: %(default)s)""")

    arg_parser.add_argument(
        '--batch-size', type=int, default=8,
        help="""Input batch size. (default: %(default)s)""")

    arg_parser.add_argument(
        '--workers', type=int, default=4,
        help="""Number of workers for loading data. (default: %(default)s)""")

    arg_parser.add_argument(
        '--seed', type=int, help="""Create a random seed.""")

    # arg_parser.add_argument(
    #     '--runs-dir', help="""Save tensor board logs to this directory.""")

    args = arg_parser.parse_args()

    # Wee need something for the data loaders
    args.seed = args.seed if args.seed is not None else randint(0, 4_000_000_000)

    return args


if __name__ == '__main__':
    started()

    ARGS = parse_args()
    train(ARGS)

    finished()
