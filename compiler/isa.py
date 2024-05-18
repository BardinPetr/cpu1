# class Instruction:
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Optional


@dataclass
class Instruction:
    opcode: 'Opcode'
    stack: Optional[int] = 0

    def __repr__(self):
        return str(self)

    def str_stack(self):
        return '@R' if self.stack != 0 else ""

    def __str__(self):
        return f"<{self.opcode}{self.str_stack()}>"


Instr = Instruction


@dataclass
class ImmInstr(Instruction):
    imm: int = 0

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
    INC = auto()
    DEC = auto()
    NEG = auto()

    # comparison
    CEQ = auto()
    CLT = auto()
    CGT = auto()

    # stack
    IPUSH = auto()
    STKMV = auto()  # stack_id is source stack
    STKCP = auto()
    STKPOP = auto()
    STKOVR = auto()
    STKDUP = auto()
    STKDRP = auto()
    STKSWP = auto()
    STKTOP = auto()

    # memory
    FETCH = auto()
    STORE = auto()
    # INCSTORE = auto()

    # jumps
    JMP = auto()  # absolute on stack
    IJMP = auto()  # relative immediate
    IJMPF = auto()  # relative immediate jump if stack is false
    IJMPT = auto()  # relative immediate jump if stack is true

    # functions
    CALL = auto()  # absolute on stack
    ICALL = auto()  # relative immediate
    RET = auto()

    # IO
    IN = auto()
    OUT = auto()

    # control
    NOP = auto()
    HLT = auto()
