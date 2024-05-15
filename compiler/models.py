from dataclasses import dataclass
from typing import Optional, List, Dict

from compiler.isa import Instruction


@dataclass
class ForthVariable:
    name: str
    loc: int
    size_slots: int
    init_value: Optional[List[int]] = None

    def __post_init__(self):
        assert not self.init_value or len(self.init_value) == self.size_slots


@dataclass
class ForthFunction:
    name: str
    loc: int
    code: List[Instruction]

    def __post_init__(self):
        self.size_slots = len(self.code) * 1


@dataclass
class ForthCode:
    code: List[Instruction]
    variables: Dict[str, ForthVariable]
    functions: Dict[str, ForthFunction]


Instructions = List[Instruction]
