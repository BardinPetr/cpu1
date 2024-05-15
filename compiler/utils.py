from dataclasses import dataclass
from functools import reduce
from hashlib import sha1
from typing import List, Union, Tuple, Iterable

from compiler.isa import Instruction


@dataclass
class Synthetic:
    contents: Tuple[Union[Instruction, 'Synthetic']]

    def unwrap(self) -> List[Instruction]:
        return reduce(
            lambda acc, i: acc + (i.unwrap() if isinstance(i, Synthetic) else [i]),
            self.contents, []
        )

    @staticmethod
    def one(instr: Instruction) -> 'Synthetic':
        return Synthetic((instr,))

    @staticmethod
    def many(*instr: Union[Instruction, 'Synthetic']) -> 'Synthetic':
        return Synthetic(instr)


Syn = Synthetic


def unwrap_code(code: Union[Iterable, Synthetic]) -> List[Instruction]:
    if not isinstance(code, Synthetic):
        code = Synthetic.many(*code)
    return code.unwrap()


def const_string_var_name(string: str) -> str:
    return "cstr_sha1_" + sha1(string.encode()).digest().hex()
