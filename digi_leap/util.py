"""Common utilities for the project."""


class DotDict(dict):
    """Allow dot.notation access to dictionary items."""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
