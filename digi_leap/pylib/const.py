"""Define literals used in the system."""
import os
from pathlib import Path

CURR_DIR = Path(os.getcwd())
IS_SUBDIR = CURR_DIR.name in ("notebooks", "experiments")
ROOT_DIR = Path(".." if IS_SUBDIR else ".")

CONFIG_PATH = ROOT_DIR / "digi_leap.yaml"
