#!/usr/bin/env python3
import argparse
import textwrap
from collections import namedtuple
from pathlib import Path

ROOT = Path(".")
MAKE_FILE = ROOT / "Makefile"
SRC = ROOT / "digi_leap"

SUB = 4  # Index of the subtree dir in the "git subtree pull" command

Script = namedtuple("Script", "tree dst")


def main():
    args = parse_args()
    clean_symlinks(args.no_clean)
    sub_trees = get_subtrees()
    scripts = get_scripts(sub_trees)
    make_symlinks(scripts, args.no_create)


def make_symlinks(scripts, no_create) -> None:
    if not no_create:
        for script in scripts:
            src = SRC / script.dst.name
            dst = Path("..") / script.tree / script.tree / script.dst.name
            src.symlink_to(dst)


def get_subtrees() -> list[str]:
    with open(MAKE_FILE) as f:
        return [ln.split()[SUB] for ln in f.readlines() if ln.find("subtree pull") > -1]


def get_scripts(sub_trees) -> list[Script]:
    scripts = []
    for tree in sub_trees:
        path = ROOT / tree / tree
        for script in [p for p in path.glob("*.py") if not p.stem.startswith("__")]:
            scripts.append(Script(tree, script))
    return scripts


def clean_symlinks(no_clean) -> None:
    if not no_clean:
        for link in [lnk for lnk in SRC.glob("*.py") if lnk.is_symlink()]:
            link.unlink()


def parse_args():
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Create symlinks for all scripts in subtrees.
            Scripts starting with "__" will be skipped.
            """
        ),
    )

    arg_parser.add_argument(
        "--no-clean",
        action="store_true",
        help="""Do not remove old symlinks before creating new ones.""",
    )

    arg_parser.add_argument(
        "--no-create",
        action="store_true",
        help="""Do not create new symlinks.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
