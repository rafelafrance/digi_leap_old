"""A class to hold data parsed from PDFs."""
from dataclasses import dataclass
from dataclasses import field


@dataclass
class Datum:
    """A class to hold data parsed from PDFs."""

    text: str = ""
    traits: list[dict] = field(default_factory=list)
