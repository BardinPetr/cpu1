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
    code: List[Instruction]
    loc: Optional[int] = None
    is_inline: bool = False

    def __post_init__(self):
        self.size_slots = len(self.code) * 1

    @staticmethod
    def inline(name: str, code: List[Instruction]) -> 'ForthFunction':
        return ForthFunction(name, code, is_inline=True)

    @staticmethod
    def external(name: str, loc: int, code: List[Instruction]) -> 'ForthFunction':
        return ForthFunction(name, code, loc=loc, is_inline=False)


Func = ForthFunction


@dataclass
class ForthCode:
    code: List[Instruction]
    variables: Dict[str, ForthVariable]
    functions: List[ForthFunction]


Instructions = List[Instruction]
