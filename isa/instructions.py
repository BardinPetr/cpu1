from dataclasses import dataclass
from typing import Optional

from myhdl import intbv

from isa.isa import Opcode
from machine.config import INSTR_BITS


@dataclass
class Instruction:
    opcode: 'Opcode'
    stack: Optional[int] = None
    ctrl: Optional[int] = None
    imm: int = 0

    def __post_init__(self):
        self.group = self.opcode.value[0]
        self.alt = self.opcode.value[1]
        if self.ctrl is None and self.stack is not None:
            self.ctrl = self.stack

    def __repr__(self):
        return str(self)

    def str_stack(self):
        return '@R' if self.stack != 0 else ""

    def __str__(self):
        return f"<{self.opcode}{self.str_stack()}>"

    def pack(self) -> intbv:
        res = intbv()[INSTR_BITS:]
        res[16:] = self.imm
        res[16 + 4:16] = self.ctrl
        res[20 + 8:20] = self.alt
        res[28 + 4:28] = self.alt
        return res


Instr = Instruction


@dataclass
class ImmInstr(Instruction):

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{super().__str__()}(I|{self.imm})"


@dataclass
class IPRelInstr(Instruction):
    abs: Optional[int] = None
    rel: Optional[int] = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        r = self.rel if self.rel else "?"
        a = f"->{self.abs}" if self.abs else ""
        return f"{super().__str__()}(I|R{r}{a})"
