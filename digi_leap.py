#!/usr/bin/env python3
"""Run digi-leap."""

import sys
import textwrap
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path

import digi_leap.actions.faster_rcnn_test as faster_rcnn_test
import digi_leap.actions.faster_rcnn_train as faster_rcnn_train
import digi_leap.actions.faster_rcnn_use as faster_rcnn_use
import digi_leap.actions.idigbio_images as idigbio_images
import digi_leap.actions.ocr_ensemble as ocr_ensemble
import digi_leap.actions.ocr_expedition as ocr_expedition
import digi_leap.actions.ocr_in_house_qc as ocr_in_house_qc
import digi_leap.actions.ocr_labels as ocr_labels
import digi_leap.actions.ocr_prepare as ocr_prepare
import digi_leap.pylib.config as conf
import digi_leap.pylib.const as const
from digi_leap.pylib.util import kabob

DISPATCH = {
    "faster_rcnn_test": faster_rcnn_test.test,
    "faster_rcnn_train": faster_rcnn_train.train,
    "faster_rcnn_use": faster_rcnn_use.use,
    "idigbio_images": idigbio_images.download_images,
    "ocr_ensemble": ocr_ensemble.build_all_ensembles,
    "ocr_expedition": ocr_expedition.build_expedition,
    "ocr_in_house_qc": ocr_in_house_qc.sample_sheets,
    "ocr_labels": ocr_labels.ocr_labels,
    "ocr_prepare": ocr_prepare.prepare_labels,
}


def parse_args(configs) -> Namespace:
    """Process the command-line."""
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Digi-Leap extracts information from from labels on images of herbarium
            sheets. It searches for labels on the sheets, extracts them, OCRs the
            labels, and extracts information from the OCR text.
            """
        )
    )

    subparsers = parser.add_subparsers()

    list_params(subparsers)

    for key, value in configs.items():
        if isinstance(value, conf.Config):
            continue
        add_subparser(subparsers, configs[key], key)

    args = parser.parse_args()
    return args


def add_subparser(subparsers, section, name):
    """Add a subparser for a module."""
    subparser = subparsers.add_parser(kabob(name), help=section.get("help"))
    subparser.set_defaults(func=name)

    for key, config in section.items():
        if isinstance(config, conf.Config):
            arg_dict = config.argument_dict()
            subparser.add_argument(f"--{kabob(key)}", **arg_dict)


def list_params(subparsers):
    """Add a list parameter values."""

    def func(args, configs):
        """Perform the list params action."""
        if args.action == "all":
            conf.display(configs)
        else:
            try:
                sect = configs[args.action]
            except KeyError:
                sys.exit(f"Could not find action: {args.action}")
            print(args.action)
            conf.display(sect)

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
    configs = conf.read_configs(const.CONFIG_PATH)

    args = parse_args(configs)

    if not hasattr(args, "func"):
        name = Path(sys.argv[0]).name
        sys.exit(f"You need to choose an action. See: {name} -h")

    if args.func in DISPATCH:
        DISPATCH[args.func](args)
    else:
        args.func(args, configs)


if __name__ == "__main__":
    main()
