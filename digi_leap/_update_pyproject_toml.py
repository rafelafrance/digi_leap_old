#!/usr/bin/env python3
import argparse
import textwrap
from pathlib import Path

import tomlkit

ROOT = Path()
MAKE_FILE = ROOT / "Makefile"
NAME = "pyproject.toml"
PYPROJECT_TOML = ROOT / NAME
"https://github.com/rafelafrance/FloraTraiter/blob/main/pyproject.toml"

DEPS = tomlkit.array('["tomlkit"]')

SUB = 5  # Index of the subtree URL in the "git remote add" command


def main():
    _args = parse_args()

    # with PYPROJECT_TOML.open() as fp:
    #     pyproject = tomlkit.load(fp)
    # deps = set(pyproject["project"]["dependencies"])
    #
    # for tree in get_subtrees():
    #     path = ROOT / tree / NAME
    #     with path.open() as fp:
    #         subproject = tomlkit.load(fp)
    #     deps |= set(subproject["project"]["dependencies"])
    #
    # pyproject["project"]["dependencies"] = tomlkit.array()
    # for dep in sorted(deps):
    #     pyproject["project"]["dependencies"].add_line(dep)
    #
    # with PYPROJECT_TOML.open("w") as fp:
    #     tomlkit.dump(pyproject, fp)


def get_subtrees() -> list[str]:
    with MAKE_FILE.open() as f:
        return [ln.split()[SUB] for ln in f.readlines() if ln.find("subtree pull") > -1]


def parse_args():
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Update pyproject.toml with dependencies from subtrees.

            It finds the subtrees and downloads the pyproject.toml for each and builds a
            combined dependencies section from all of the subtree versions.
            """,
        ),
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
