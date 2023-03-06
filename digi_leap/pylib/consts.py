import os
from pathlib import Path

from .traits import vocabulary as vocab


CURR_DIR = Path(os.getcwd())
IS_SUBDIR = CURR_DIR.name in ("notebooks", "experiments", "junk")
ROOT_DIR = Path(".." if IS_SUBDIR else ".")
VOCAB_DIR = Path(vocab.__file__).parent

DATA_DIR = ROOT_DIR / "data"
MOCK_DIR = ROOT_DIR / "tests" / "mock_data"
VOCAB_DB = ROOT_DIR / "data" / "vocab.sqlite"
CHAR_DB = (
    ROOT_DIR
    / "digi_leap"
    / "pylib"
    / "builder"
    / "line_align"
    / "char_sub_matrix.sqlite"
)

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD_DEV = (0.229, 0.224, 0.225)


CLASSES = "Other Typewritten ".split()
# CLASSES = "Other Barcode Both Handwritten Typewritten".split()
# CLASSES = "Typewritten Handwritten Barcode Both Other".split()  # For Label Babel 2
# CLASSES = "None Barcode Both Handwritten Typewritten".split()

CLASS2INT = {c: i for i, c in enumerate(CLASSES)}
CLASS2NAME = {v: k for k, v in CLASS2INT.items()}

CHARS = r"""
    ! " # % & ' ( ) * + , - . /
    0 1 2 3 4 5 6 7 8 9
    : ; < = > ? @
    A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
    [ \ ] ^ _ `
    a b c d e f g h i j k l m n o p q r s t u v w x y z
    { } ~ ° é — ‘ ’ “ ” ™
    ¼ ½ ¾ ⅓ ⅔ ×
    """
CHARS = "".join(["\n", " ", *CHARS.split()])
