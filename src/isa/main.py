from enum import auto
from typing import List

from isa.model.instructions import Instruction
from src.isa.model.opcodes import OpcodeEnum, OpcodeGroupEnum


class OpcodeGroup(OpcodeGroupEnum):
    GIOC = 0
    GMTH = auto()
    GSTK = auto()
    GCMP = auto()
    GJMP = auto()
    GMEM = auto()


class Opcode(OpcodeEnum):
    """
    Stores opcode as pair (group, alt)
    """

    """ OpcodeGroup.GMTH """
    ADD = OpcodeGroup.GMTH, 0
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

    """ OpcodeGroup.GCMP """
    CLTU = OpcodeGroup.GCMP, 0
    CGTU = auto()
    CLTS = auto()
    CGTS = auto()
    CEQ = auto()

    """ OpcodeGroup.GSTK """
    ISTKPSH = OpcodeGroup.GSTK, 0
    STKMV = auto()  # stack_id is source stack
    STKCP = auto()
    STKPOP = auto()
    STKOVR = auto()
    STKDUP = auto()
    STKSWP = auto()

    """ OpcodeGroup.GMEM """
    FETCH = OpcodeGroup.GMEM, 0
    STORE = auto()

    """ OpcodeGroup.GJMP """
    # jumps
    JMP = OpcodeGroup.GJMP, 0  # absolute on stack
    IJMP = auto()  # relative immediate
    IJMPF = auto()  # relative immediate jump if stack is false
    IJMPT = auto()  # relative immediate jump if stack is true

    # functions
    CALL = auto()  # absolute on stack
    ICALL = auto()  # relative immediate
    RET = auto()

    """ OpcodeGroup.GIOC """
    # control
    HLT = OpcodeGroup.GIOC, 0
    NOP = auto()

    # IO
    IN = auto()
    OUT = auto()


def compile_instructions(code: List[Instruction]) -> List[int]:
    return [int(i.pack()) for i in code]


if __name__ == "__main__":
    print(f"{'OPCODE':13} |  GRP|     ALT|")
    print("-" * 28)
    for op in sorted(Opcode, key=lambda x: x.identifier):
        print(f"{op.group.name:4}.{op.name:8} : {op.group:04b} {op.alt:08b}")
