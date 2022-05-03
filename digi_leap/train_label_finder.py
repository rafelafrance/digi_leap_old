#!/usr/bin/env python3
"""Train a model to cut out labels on herbarium sheets."""
import argparse
import textwrap
from pathlib import Path

from pylib import consts
from pylib import log
from pylib.label_finder.models import efficient_det_model as edm
from pylib.label_finder.runners import trainer_runner


def main():
    log.started()
    args = parse_args()
    model = edm.create_model(
        len(consts.CLASSES), name=args.model, image_size=args.image_size
    )
    trainer_runner.train(model, args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Train a model to find labels on herbarium sheets."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--save-model",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Save best models to this path.""",
    )

    arg_parser.add_argument(
        "--load-model",
        type=Path,
        metavar="PATH",
        help="""Path model to continue training.""",
    )

    arg_parser.add_argument(
        "--model",
        default="tf_efficientnetv2_s",
        help="""What model to use as the object detector. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--image-size",
        type=int,
        metavar="PIXELS",
        default=384,  # To work with the default model
        help="""Set the image size to this. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--label-set",
        metavar="NAME",
        required=True,
        help="""Which which labels to use.""",
    )

    arg_parser.add_argument(
        "--learning-rate",
        "--lr",
        type=float,
        metavar="FLOAT",
        default=0.001,
        help="""Initial learning rate. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--batch-size",
        type=int,
        metavar="INT",
        default=16,
        help="""Input batch size. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--workers",
        type=int,
        metavar="INT",
        default=4,
        help="""Number of workers for loading data. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--epochs",
        type=int,
        metavar="INT",
        default=100,
        help="""How many epochs to train. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--log-dir",
        type=Path,
        metavar="DIR",
        help="""Save tensorboard logs to this directory.""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run.""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    main()
