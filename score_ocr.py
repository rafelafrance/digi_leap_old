#!/usr/bin/env python
"""Score the OCR output."""

import re
import string
import textwrap
from argparse import ArgumentParser, Namespace
from pathlib import Path

import enchant
import pandas as pd
from tqdm import tqdm

from digi_leap.log import finished, started

PUNCT = re.escape(string.punctuation)
SPLIT = re.compile(rf"([\s{PUNCT}]+)")

ALLOW = {".)", ".]"}


def score_results(args):
    """Score the OCR results as best we can."""
    results = []
    vocab = spell_checker(args)
    paths = sorted(args.text_dir.glob("*.txt"))
    # tokenizer = get_tokenizer(args.lang)
    for path in tqdm(paths):
        with open(path) as in_file:
            text = in_file.read()

        words = [x for w in SPLIT.split(text) if (x := w.strip())]
        found = 0
        for word in words:
            ok = vocab.check(word)
            if not ok and (len(word) == 1 or word in ALLOW):
                ok = True
            if ok:
                found += 1

        total = len(words)
        missing = total - found
        percent = round(missing / total * 100.0, 2) if total != 0.0 else 100.0

        results.append(
            {
                "file": str(path),
                "stem": path.stem,
                "total": total,
                "found": found,
                "missing": missing,
                "missing percent": percent,
            }
        )

    df = pd.DataFrame(results)
    df.to_csv(args.scores, index=False)


def spell_checker(args):
    """Setup the spell checker."""
    if args.extra_vocab:
        vocab = enchant.DictWithPWL(args.lang, str(args.extra_vocab))
    else:
        vocab = enchant.Dict(args.lang)
    return vocab


def parse_args() -> Namespace:
    """Process command-line arguments."""
    description = """Score OCR results."""
    arg_parser = ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--text-dir",
        "-t",
        type=Path,
        required=True,
        help="""The directory where the OCR results are.""",
    )

    arg_parser.add_argument(
        "--scores",
        "-s",
        type=Path,
        required=True,
        help="""Output the scores to this CSV file.""",
    )

    arg_parser.add_argument(
        "--extra-vocab", "-v", type=Path, help="""An extra vocabulary file."""
    )

    arg_parser.add_argument(
        "--lang",
        "-l",
        default="en_US",
        help="""Which language to use. (default: %(default)s)""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    started()

    ARGS = parse_args()
    score_results(ARGS)

    finished()
