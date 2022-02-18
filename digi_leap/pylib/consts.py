"""Define literals used in the system."""
import os
from pathlib import Path

CURR_DIR = Path(os.getcwd())
IS_SUBDIR = CURR_DIR.name in ("notebooks", "experiments")
ROOT_DIR = Path(".." if IS_SUBDIR else ".")

CONFIG_PATH = ROOT_DIR / "digi_leap.yaml"


IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD_DEV = (0.229, 0.224, 0.225)


CLASSES = "None Barcode Both Handwritten Typewritten".split()
CLASS2INT = {c: i for i, c in enumerate(CLASSES, 1)}
CLASS2NAME = {v: k for k, v in CLASS2INT.items()}
