from dataclasses import dataclass
from typing import List, TypeAlias

@dataclass
class Example:
    input: str
    output: str

@dataclass
class Style:
    name: str
    examples: List[Example]

Styles: TypeAlias = List[Style]
