"""Find "best" labels from ensembles of OCR results of each label."""

import re
from argparse import Namespace
from pathlib import Path

import digi_leap.pylib.ensemble as ensemble


def build_all_ensembles(args: Namespace) -> None:
    """Group OCR output paths by label."""
    ensemble.create_dirs(args.ensemble_image_dir, args.ensemble_text_dir)

    paths = ensemble.group_files(args.ocr_dir)
    paths = filter_files(paths, args.limit, args.label_filter)

    ensemble.process_batches(
        paths,
        args.batch_size,
        args.cpus,
        args.prepared_label_dir,
        args.ensemble_text_dir,
        args.ensemble_image_dir,
        args.line_space,
    )


def filter_files(paths, limit, label_filter) -> list[tuple[str, list[Path]]]:
    """Filter files for debugging specific images."""
    if label_filter:
        paths = [(k, v) for k, v in paths if re.search(label_filter, k)]
    paths = paths[:limit] if limit else paths
    return paths

# def parse_args() -> Namespace:
#     """Process command-line arguments."""
#     description = """
#         Build a single "best" label from the ensemble of OCR outputs.
#
#         An ensemble is a list of OCR outputs with the same name contained
#         in parallel directories. For instance, if you have OCR output
#         (from ocr_labels.py) for three different runs then an ensemble
#         will be:
#             output/ocr/run1/label1.csv
#             output/ocr/run2/label1.csv
#             output/ocr/run3/label1.csv
#         """
#     arg_parser = ArgumentParser(
#         formatter_class=RawDescriptionHelpFormatter,
#         description=textwrap.dedent(description),
#         fromfile_prefix_chars="@",
#     )
#
#     defaults = Config().module_defaults()
#
#     arg_parser.add_argument(
#         "--ocr-dir",
#         default=defaults.ocr_dir,
#         nargs="*",
#         help="""A directory that contains OCR output in CSV form. You may use
#             wildcards and/or more than one filter. (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--prepared-label-dir",
#         default=defaults.prep_deskew_dir,
#         type=Path,
#         help="""The directory containing images of labels ready for OCR.
#             (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--ensemble-image-dir",
#         default=defaults.ensemble_image_dir,
#         type=Path,
#         help="""Output resulting images of the OCR ensembles to this directory.
#              (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--ensemble-text-dir",
#         default=defaults.ensemble_text_dir,
#         type=Path,
#         help="""Output resulting text of the OCR ensembles to this directory.
#              (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--cpus",
#         default=defaults.proc_cpus,
#         type=int,
#         help="""How many CPUs to use. (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--batch-size",
#         default=defaults.proc_batch,
#         type=int,
#         help="""How many labels to process in a process batch. (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--line_space",
#         type=int,
#         default=defaults.line_space,
#         help="""Margin between lines of text in the reconstructed label output.
#             (default %(default)s)""",
#     )
#
#     arg_parser.add_argument(
#         "--limit",
#         type=int,
#         help="""Limit the input to this many label images.""",
#     )
#
#     arg_parser.add_argument(
#         "--label-filter",
#         type=str,
#         help="""Filter files in the --prepared-dir and --ocr-dir with this.
#             (default %(default)s)""",
#     )
#
#     args = arg_parser.parse_args()
#     return args
#
#
# if __name__ == "__main__":
#     log.started()
#
#     ARGS = parse_args()
#     build_all_ensembles(ARGS)
#
#     log.finished()
