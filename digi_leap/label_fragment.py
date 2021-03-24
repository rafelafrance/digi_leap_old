"""A label fragment class."""

from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Optional

Use = Enum('Use', """auth catalog_number date field_label lat_long name rights_holder
    sci_name text title verbatim""")
Writing = Enum('Writing', """typewritten handwritten barcode qrcode""")
LabelType = Enum('LabelType', 'main determiner barcode qrcode')

Size = namedtuple('TextSize', 'width height')


@dataclass
class LabelFragment:
    """Holds bits of text and its image."""
    label_id: str
    label_type: LabelType
    writing: Writing
    row: int
    col: int
    text: str
    use: Use
    line: int = 0
    font: Optional[str] = None
    text_size: Optional[Size] = None


def db2fragment(db_rec: dict) -> LabelFragment:
    """Convert a database label record to a label fragment object."""
    return LabelFragment(
        label_id=db_rec['label_id'],
        label_type=db_rec['label_type'],
        writing=Writing[db_rec['writing']],
        row=db_rec['row'],
        col=db_rec['col'],
        text=db_rec['text'],
        use=Use[db_rec['use']],
        line=db_rec['line'],
    )
