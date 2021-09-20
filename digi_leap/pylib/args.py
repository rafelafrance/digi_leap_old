"""Common arguments.

This is an experiment to see if a central place for command-line arguments will help
DRY things up a bit.
"""

import argparse
import textwrap
from pathlib import Path

from . import subject
from .config import Config


class ArgParser:
    """Argument parser."""

    def __init__(self, description=""):
        self.config = Config()
        self.defaults = self.config.module_defaults()
        self.parser = argparse.ArgumentParser(
            description=textwrap.dedent(description), fromfile_prefix_chars="@"
        )

    def parse_args(self):
        """Parse the arguments."""
        return self.parser.parse_args()

    # #################################################################################
    # Directories

    def ensemble_image_dir(self):
        """Create an argument for where the ensemble image results are stored."""
        self.parser.add_argument(
            "--ensemble-image-dir",
            default=self.defaults.ensemble_image_dir,
            type=Path,
            metavar="DIR",
            help="""Get images of the OCR ensemble results from this directory.
                 (default %(default)s)""",
        )

    def ensemble_text_dir(self):
        """Create an argument for where the ensemble text results are stored."""
        self.parser.add_argument(
            "--ensemble-text-dir",
            default=self.defaults.ensemble_text_dir,
            type=Path,
            metavar="DIR",
            help="""Get text of the OCR ensemble results from this directory.
                 (default %(default)s)""",
        )

    def expedition_dir(self):
        """Create an argument for where to write the expedition contents."""
        self.parser.add_argument(
            "--expedition-dir",
            default=self.defaults.expedition_dir,
            type=Path,
            metavar="DIR",
            help="""Write the OCR ensembles results to this directory.
                 (default %(default)s)""",
        )

    def label_dir(self, action="read write"):
        """Create an output directory for labels argument."""
        prep = "from" if action == "read" else "to"
        self.parser.add_argument(
            "--label-dir",
            default=self.defaults.label_dir,
            type=Path,
            metavar="DIR",
            help=f"""{action.capitalize()} cropped labels {prep} this directory.
                (default %(default)s)""",
        )

    def sheets_dir(self):
        """Create an argument for the herbarium sheets directory."""
        self.parser.add_argument(
            "--sheets-dir",
            default=self.defaults.sheets_dir,
            type=Path,
            metavar="DIR",
            help="""A directory containing the herbarium sheet images corresponding
                to the --reconciled-jsonl file from  this directory.
                (default %(default)s)""",
        )

    # #################################################################################

    def reconciled_jsonl(self):
        """Create a argument for the reconciled JSONL file."""
        self.parser.add_argument(
            "--reconciled-jsonl",
            default=self.defaults.reconciled_jsonl,
            type=Path,
            metavar="JSONL",
            help="""The JSONL file containing reconciled bounding boxes of labels.
                (default %(default)s)""",
        )

    def curr_model(self, action="load save"):
        """Create an argument to load or save a model."""
        self.parser.add_argument(
            f"--{action}-model",
            dest="curr_model",
            default=self.defaults.curr_model,
            type=Path,
            metavar="MODEL",
            help=f"""{action.capitalize()} this model. (default %(default)s)""",
        )

    def prev_model(self):
        """Create an argument to load a model to continue training."""
        self.parser.add_argument(
            "--load-model",
            dest="prev_model",
            type=Path,
            metavar="MODEL",
            help="""Load this model to continue training.
                (default %(default)s)""",
        )

    def device(self):
        """Create an argument for the GPU device."""
        self.parser.add_argument(
            "--device",
            default=self.defaults.device,
            help="""Which GPU or CPU to use. Options are 'cpu', 'cuda:0',
                'cuda:1', etc. (default: %(default)s)""",
        )

    def gpu_batch(self):
        """Create an argument for the GPU batch size."""
        self.parser.add_argument(
            "--batch-size",
            default=self.defaults.gpu_batch,
            type=int,
            metavar="N",
            help="""Input batch size. (default: %(default)s)""",
        )

    def workers(self):
        """Create an argument for the number of GPU batch processes."""
        self.parser.add_argument(
            "--workers",
            default=self.defaults.workers,
            type=int,
            metavar="N",
            help="""Number of workers for loading data. (default: %(default)s)""",
        )

    def nms_threshold(self):
        """Create an argument for the non-maximum suppression IoU threshold."""
        self.parser.add_argument(
            "--nms-threshold",
            default=self.defaults.nms_threshold,
            type=float,
            metavar="THRESHOLD",
            help="""The IoU threshold to use for non-maximum suppression. (0.0 - 1.0].
                (default: %(default)s)""",
        )

    def sbs_threshold(self):
        """Create an argument for the small box suppression IoU threshold."""
        self.parser.add_argument(
            "--sbs-threshold",
            default=self.defaults.sbs_threshold,
            type=float,
            metavar="THRESHOLD",
            help="""The area threshold to use for small box suppression (0.0 - 1.0].
                (default: %(default)s)""",
        )

    def limit(self):
        """Create an argument to limit the input records."""
        self.parser.add_argument(
            "--limit",
            type=int,
            metavar="N",
            help="""Limit the input to this many records.""",
        )

    def split(self):
        """Create a train:score ratio split argument."""
        self.parser.add_argument(
            "--split",
            default=self.defaults.split,
            type=float,
            metavar="FRACTION",
            help="""Fraction of subjects in the score dataset.
                (default: %(default)s)""",
        )

    def epochs(self):
        """Create an training epochs count argument."""
        self.parser.add_argument(
            "--epochs",
            type=int,
            default=self.defaults.epochs,
            metavar="N",
            help="""How many epochs to train. (default: %(default)s)""",
        )

    def learning_rate(self):
        """Create a model learning rate argument."""
        self.parser.add_argument(
            "--learning-rate",
            type=float,
            default=self.defaults.learning_rate,
            metavar="RATE",
            help="""Initial learning rate. (default: %(default)s)""",
        )

    def image_filter(self):
        """Create an image filter (glob) argument."""
        self.parser.add_argument(
            "--image-filter",
            default=self.defaults.image_filter,
            metavar="PATTERN",
            help="""Use images in the --image-dir with this glob pattern.
                (default: %(default)s)""",
        )

    def filter_rulers(self):
        """Create an argument for the width to height ratio for deleting rulers."""
        self.parser.add_argument(
            "--filter-rulers",
            default=self.defaults.filter_rulers,
            type=float,
            metavar="RATIO",
            help="""Remove rulers where the width to height (or vice vera) ratio is
                greater than the given threshold. (default %(default)s)""",
        )

    def largest_labels(self):
        """Create an argument for how many labels to keep."""
        self.parser.add_argument(
            "--largest-labels",
            default=self.defaults.largest_labels,
            type=int,
            metavar="N",
            help="""Keep the N labels with the highest word count.
                (default %(default)s)""",
        )

    def filter_types(self):
        """Create an argument to filter labels by type."""
        default = " ".join(self.config.default_list("filter_types"))
        choices = subject.CLASSES
        self.parser.add_argument(
            "--filter-types",
            choices=choices,
            default=default,
            help="""Remove these types of labels. (default %(default)s)""",
        )

    def word_threshold(self):
        """Create an argument for threshold that turns filtering to image size."""
        self.parser.add_argument(
            "--word-threshold",
            default=self.defaults.word_threshold,
            type=int,
            metavar="N",
            help="""When filtering by size if the label with the maximum word count has
                fewer than this many words then switch to filter the labels by image
                size. (default %(default)s)""",
        )
