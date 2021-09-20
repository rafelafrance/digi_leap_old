"""Utilities for working with configurations."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml

from . import const


@dataclass
class Config:
    """A config setting with help."""
    default: Any
    help: str


def read_configs(path: Optional[Path] = None):
    """Read settings from a YAML file."""
    path = path if path else const.CONFIG_PATH
    configs = read_yaml_file(path)
    string_replace(configs)
    return configs


def read_yaml_file(path):
    """Build the data from the config file."""
    loader = yaml.SafeLoader
    loader.add_constructor("!Config", config_constructor)
    loader.add_constructor("!Path", path_constructor)
    configs = yaml.load(open(path, "rb"), loader)
    return configs


def config_constructor(loader, node):
    """Load a !Config tag."""
    return Config(**loader.construct_mapping(node))


def path_constructor(loader, node):
    """Load a !Path tag."""
    value = str(loader.construct_scalar(node))
    return Path(value)


def string_replace(configs):
    """Do string substitutions of the YAML variables."""
    # It's hacky, but I don't need more than this yet. Problems:
    #   - Only handles one level of objects. Make it recursive.
    #   - Branching on isinstance()
    for key, value in configs.items():
        if isinstance(value, Config):
            configs[key].default = replace(configs, value.default)
        elif isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, Config):
                    configs[key][k].default = replace(configs, v.default)
        elif isinstance(value, list):
            for v in value:
                v.default = replace(configs, v.default)


def replace(configs, value):
    """Replace values in a string."""
    # Problem: This branches on isinstance()
    new = str(value)
    if matches := re.compile(r"{(\w+)}").findall(new):
        for match in matches:
            new = new.replace(f"{{{match}}}", str(configs[match].default))
        value = Path(new) if isinstance(value, Path) else new
    return value


def display(configs):
    """Format the configs for printing to the screen."""
    for key, value in configs.items():
        if isinstance(value, Config):
            print(f"    {key:<16} {value}")
        elif isinstance(value, list):
            print()
            print(key)
            for config in value:
                print("    ", config)
        elif isinstance(value, dict):
            print()
            print(key)
            for k, config in value.items():
                print(f"    {k:<16} {config}")
