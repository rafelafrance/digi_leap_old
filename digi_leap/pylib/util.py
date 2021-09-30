"""Common utilities."""

from contextlib import contextmanager
from shutil import rmtree
from tempfile import mkdtemp
from typing import Any


@contextmanager
def make_temp_dir(where=None, prefix=None, keep=False):
    """Handle creation and deletion of temporary directory in/outside of /tmp."""
    temp_dir = mkdtemp(prefix=prefix, dir=where)
    try:
        yield temp_dir
    finally:
        if not keep or not where:
            rmtree(temp_dir, ignore_errors=True)


def collate_fn(batch):
    """Turn batches into tuples."""
    return tuple(zip(*batch))


def as_list(values: Any) -> list:
    """Convert values to a list."""
    return list(values) if isinstance(values, (list, tuple, set)) else [values]


def kabob(string):
    """Convert snake case to kabob case."""
    return string.replace("_", "-")
