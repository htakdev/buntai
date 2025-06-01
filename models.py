from dataclasses import dataclass
from typing import List


@dataclass
class Example:
    input: str
    output: str

@dataclass
class Style:
    name: str
    examples: List[Example]
