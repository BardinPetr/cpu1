from enum import auto

from src.isa.model.opcodes import OpcodeEnum, OpcodeGroupEnum


class OpcodeGroup(OpcodeGroupEnum):
    GMTH = 0
    GSTK = auto()
    GCMP = auto()
    GMEM = auto()
    GIOC = auto()
    GJMP = auto()


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
    CEQ = OpcodeGroup.GCMP, 0
    CLT = auto()
    CGT = auto()

    """ OpcodeGroup.GSTK """
    IPUSH = OpcodeGroup.GSTK, 0
    STKMV = auto()  # stack_id is source stack
    STKCP = auto()
    STKPOP = auto()
    STKOVR = auto()
    STKDUP = auto()
    STKDRP = auto()
    STKSWP = auto()
    STKTOP = auto()

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
    # IO
    IN = OpcodeGroup.GIOC, 0
    OUT = auto()

    # control
    NOP = auto()
    HLT = auto()


if __name__ == "__main__":
    print(f"{'OPCODE':11} |  GRP|     ALT|")
    print("-" * 28)
    for op in sorted(Opcode, key=lambda x: x.identifier):
        print(f"{op.group.name:4}.{op.name:6} : {op.group:04b} {op.alt:08b}")
