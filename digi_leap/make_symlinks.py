#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".")
MAKE_FILE = ROOT / "Makefile"
DST = ROOT / "digi_leap"

SUB = 4  # Index of the subtree dir in the "git subtree pull" command


def main():
    sub_trees = get_subtrees()
    scripts = get_scripts(sub_trees)


def get_subtrees() -> list[str]:
    with open(MAKE_FILE) as f:
        return [ln.split()[SUB] for ln in f.readlines() if ln.find("subtree pull") > -1]


def get_scripts(sub_trees) -> list[Path]:
    scripts = []
    for tree in sub_trees:
        path = ROOT / tree / tree
        for script in [p for p in path.glob("*.py") if not p.stem.startswith("__")]:
            print(script.name)
    return scripts


if __name__ == "__main__":
    main()
