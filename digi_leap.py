#!/usr/bin/env python3
"""Run digi-leap."""
import sys
import textwrap
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawDescriptionHelpFormatter
from pathlib import Path

import digi_leap.pylib.args as arguments
from digi_leap.actions import find_labels
from digi_leap.actions import idigbio_images
from digi_leap.actions import ocr_labels

# from digi_leap.actions import faster_rcnn_test
# from digi_leap.actions import faster_rcnn_train
# from digi_leap.actions import ocr_ensemble
# from digi_leap.actions import ocr_expedition
# from digi_leap.actions import ocr_in_house_qc

DISPATCH = {
    # "faster_rcnn_test": faster_rcnn_test.test,
    # "faster_rcnn_train": faster_rcnn_train.train,
    "find_labels": find_labels.find,
    "idigbio_images": idigbio_images.download_images,
    "idigbio_verify_images": idigbio_images.verify_images,
    "ocr": ocr_labels.ocr_labels,
    # "ocr_ensemble": ocr_ensemble.build_all_ensembles,
    # "ocr_expedition": ocr_expedition.build_expedition,
    # "ocr_in_house_qc": ocr_in_house_qc.sample_sheets,
}


def parse_args() -> Namespace:
    """Process the command-line."""
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Digi-Leap extracts information from from labels on images of herbarium
            sheets. It searches for labels on the sheets, extracts them, OCRs the
            labels, and extracts information from the OCR text.
            """
        ),
    )

    subparsers = parser.add_subparsers()

    list_params(subparsers)

    for key, value in arguments.ARGS.items():
        add_subparser(subparsers, key, arguments.ARGS[key])

    args = parser.parse_args()
    return args


def add_subparser(subparsers, name, section):
    """Add a subparser for a module."""
    subparser = subparsers.add_parser(name, help=section.get("help"))
    subparser.set_defaults(func=name)

    for key, config in section.items():
        if isinstance(config, dict):
            subparser.add_argument(f"--{key}", **config)


def list_params(subparsers):
    """Add a list parameter values."""

    def func(args):
        """Perform the list params action."""
        if args.action != "all" and args.action not in arguments.ARGS:
            sys.exit(f"Unknown action: {args.action}")

        for action, params in arguments.ARGS.items():
            if args.action == "all" or action == args.action:
                print()
                print(action)
                arguments.display(params)

    subparser = subparsers.add_parser("list", help="""List parameters for actions.""")
    subparser.set_defaults(func=func)
    subparser.add_argument(
        "action",
        nargs="?",
        default="all",
        help="""List parameters used for a particular action. Use all to see all
            parameters.""",
    )


def main():
    """Run the script."""
    args = parse_args()
    if not hasattr(args, "func"):
        name = Path(sys.argv[0]).name
        sys.exit(f"You need to choose an action. See: {name} -h")

    if args.func in DISPATCH:
        DISPATCH[args.func](args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
