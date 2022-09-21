#!/usr/bin/env python3
"""Use a model for finding labels on herbarium sheets on unlabeled data."""
import argparse
import textwrap
from pathlib import Path

from pylib import consts
from pylib import log
from pylib.finder.engines import predictor_engine
from pylib.finder.models import efficient_det_model
from pylib.finder.models import model_utils


def main():
    log.started()
    args = parse_args()
    model = efficient_det_model.create_model(
        len(consts.CLASSES),
        name=args.model,
        image_size=args.image_size,
        pretrained=False,
    )
    predictor_engine.predict(model, args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """
        Use a trained model for finding labels on herbarium sheets on a holdout set.
        """

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--sheet-set",
        required=True,
        metavar="NAME",
        help="""Predict labels for these sheets.""",
    )

    arg_parser.add_argument(
        "--label-set",
        metavar="NAME",
        required=True,
        help="""Write labels to this set.""",
    )

    arg_parser.add_argument(
        "--load-model",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path model to continue training.""",
    )

    arg_parser.add_argument(
        "--model",
        choices=list(model_utils.MODELS.keys()),
        default=list(model_utils.MODELS.keys())[0],
        help="""What model to use as the object detector. (default: %(default)s)""",
    )

    arg_parser.add_argument(
        "--image-size",
        type=int,
        metavar="PIXELS",
        default=384,  # Matches the default model
        help="""Set the image size to this. (default: %(default)s)""",
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
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run. Enclose them in quotes.""",
    )

    args = arg_parser.parse_args()

    return args


if __name__ == "__main__":
    main()