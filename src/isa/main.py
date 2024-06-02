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
    AJMP = OpcodeGroup.GJMP, 0b000  # absolute on stack
    RJMP = auto()  # ip-relative immediate
    CJMP = auto()  # ip-relative immediate jump if stack is
    RCALL = auto()  # relative immediate
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
