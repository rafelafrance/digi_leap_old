#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

from pylib import log
from pylib.finder.engines import tester_engine_effdet
from pylib.finder.models import model_utils


def main():
    log.started()
    args = parse_args()

    model = model_utils.MODELS[args.model](args)

    # if args.model == "tf_efficientnetv2_s":
    tester_engine_effdet.evaluate(model, args)
    # else:
    #     tester_engine_fasterrcnn.evaluate(model, args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """
        Test a model for finding labels on herbarium sheets on a holdout set.
        """

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        "--db",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--load-model",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path model to continue training.""",
    )

    arg_parser.add_argument(
        "--train-set",
        metavar="NAME",
        required=True,
        help="""Which labels to use.""",
    )

    arg_parser.add_argument(
        "--test-set",
        metavar="NAME",
        required=True,
        help="""Name this label finder test set.""",
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
        default=384,  # To match with the default model
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
