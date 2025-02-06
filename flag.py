from dataclasses import dataclass

from division import Division


@dataclass
class Flag:
    name: str
    category: str
    background_color: list | tuple
    divisions: list[Division]
