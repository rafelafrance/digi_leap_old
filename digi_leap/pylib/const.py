"""Define literals used in the system."""

import os
from pathlib import Path

import numpy as np

PROC_BATCH = 10

# Directories and files
CURR_DIR = Path(os.getcwd())
IS_SUBDIR = CURR_DIR.name in ("notebooks", "experiments")
ROOT_DIR = Path(".." if IS_SUBDIR else ".")

FONTS_DIR = ROOT_DIR / "fonts"

# Graphics defaults
NEAR_HORIZ = np.deg2rad(HORIZ_ANGLES)
NEAR_VERT = np.deg2rad(np.linspace(88.0, 92.0, num=9))
NEAR_HORIZ, NEAR_VERT = NEAR_VERT, NEAR_HORIZ  # ?!
