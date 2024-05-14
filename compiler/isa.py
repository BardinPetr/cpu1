# class Instruction:
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Optional


@dataclass
class Instruction:
    opcode: 'Opcode'

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"<{self.opcode}>"


Instr = Instruction


@dataclass
class ImmInstr(Instruction):
    imm: int

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"<{self.opcode}>(I|{self.imm})"


@dataclass
class IPRelInstr(Instruction):
    abs: Optional[int] = None
    rel: Optional[int] = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        r = self.rel if self.rel else "?"
        a = f"->{self.abs}" if self.abs else ""
        return f"<{self.opcode}>(I|R{r}{a})"


class Opcode(StrEnum):
    # maths
    ADD = auto()
    SUB = auto()
    DIV = auto()
    MUL = auto()
    MOD = auto()
    AND = auto()
    OR = auto()
    INV = auto()

    # comparison
    CEQ = auto()
    CLT = auto()
    CGT = auto()

    # stack
    IPUSH = auto()

    # memory
    FETCH = auto()
    STORE = auto()
    INCSTORE = auto()

    # jumps
    JMP = auto()  # absolute on stack
    IJMP = auto()  # relative immediate
    IJMPF = auto()  # relative immediate jump if stack is false
    IJMPT = auto()  # relative immediate jump if stack is true

    # functions
    CALL = auto()  # absolute on stack
    ICALL = auto()  # relative immediate
    RET = auto()

    # loops
    # TODO

    # IO
    IN = auto()
    OUT = auto()

    # control
    NOP = auto()
    HLT = auto()
