"""Utilities for working with configurations."""

import sys
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path
from typing import Optional

from . import const


class Configs:
    """Handle configurations."""

    default_path = const.ROOT_DIR / 'digi_leap.cfg'

    def __init__(self, path: Optional[Path] = None):
        path = path if path else self.default_path
        self.configs = self.read_file(path)
        self.module = Path(sys.argv[0]).stem

    @staticmethod
    def read_file(path):
        """Read data from config file."""
        configs = ConfigParser(interpolation=ExtendedInterpolation())

        with open(path) as cfg_file:
            configs.read_file(cfg_file)

        return configs

    def module_defaults(self):
        """Get argument module_defaults."""
        return self.configs[self.module]

    def default_list(self, key, section=''):
        """Make a list from a multi-line configuration."""
        section = section if section else self.module
        return self.configs[section][key].splitlines()
