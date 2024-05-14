# class Instruction:
from dataclasses import dataclass
from enum import StrEnum, auto


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
        return f"<{self.opcode}>(I{self.imm})"


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
    CJMP = auto()  # relative immediate jump if stack is true

    # functions
    CALL = auto()  # absolute on stack
    ICALL = auto()  # relative immediate
    RET = auto()

    # loops
    # TODO

    # IO
    # TODO

    # control
    NOP = auto()
    HLT = auto()
