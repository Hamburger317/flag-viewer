
from dataclasses import dataclass
from fractions import Fraction

from position import Position


@dataclass
class Division:
    position: Position
    orientation: str
    color: list | tuple
    reverse: bool = False


@dataclass
class DivisionGuide:
    fraction: Fraction
    orientation: str
    reverse: bool = False
