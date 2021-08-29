"""Define literals used in the system."""

import os
from pathlib import Path

PROC_BATCH = 10

CURR_DIR = Path(os.getcwd())
IS_SUBDIR = CURR_DIR.name in ("notebooks", "experiments")
ROOT_DIR = Path(".." if IS_SUBDIR else ".")

FONTS_DIR = ROOT_DIR / "fonts"
