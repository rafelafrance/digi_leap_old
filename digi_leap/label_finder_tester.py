#!/usr/bin/env python3
"""Test a model for finding labels on herbarium sheets on a holdout set."""
import argparse
import textwrap
from pathlib import Path

from pylib import consts
from pylib import log

from digi_leap.pylib.label_finder.models import efficient_det_model
from digi_leap.pylib.label_finder.runners import training_runner


def main():
    """Find labels on a herbarium sheet."""
    log.started()
    args = parse_args()
    model = efficient_det_model.create_model(
        len(consts.CLASSES), name=args.model, image_size=args.image_size
    )
    training_runner.train(model, args)
    log.finished()


def parse_args() -> argparse.Namespace:
    """Process command-line arguments."""
    description = """
        Test a model for finding labels on herbarium sheets on a holdout set.
    """

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        "--db",
        type=Path,
        required=True,
        metavar="PATH",
        help="""Path to the digi-leap database.""",
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
        "--limit",
        type=int,
        help="""Limit the input to this many input herbarium images.""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    main()
