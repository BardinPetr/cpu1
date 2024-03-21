"""
CMD
[16:12] =4  OR  alu_flag_ctrl
[12:8]  =4  OR  alu_port_ctrl_b
[8:4]   =4  OR  alu_port_ctrl_a
[4:0]   =4  BIN alu_ctrl


JMP
24:23  23:11    11:10   10:2    2:0
typ    target   cmp_val cmp_bit cmp_reg

"""

from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Any, TypeVar, Generic

from myhdl import intbv

from src.components.ALU import ALUCtrl, ALUPortCtrl, ALUFlagCtrl
from src.config import MC_INSTR_SZ

T = TypeVar('T', bound=IntEnum)


class MCSelectType(Enum):
    SINGLE = 0
    MULTIPLE = 1


class MCLocator:

    def __init__(self, loc_start, loc_end, select=MCSelectType.SINGLE):
        self.loc_start = loc_start
        self.loc_end = loc_end
        self.select = select

    def put(self, target: intbv, source):
        target[self.loc_end:self.loc_start] = source

    def get(self, source: intbv) -> intbv:
        return source[self.loc_end:self.loc_start]

    @property
    def size(self):
        return self.loc_end - self.loc_start


MCALUCtrl = MCLocator(0, 4)
MCALUPortACtrl = MCLocator(4, 8)
MCALUPortBCtrl = MCLocator(8, 12)
MCALUFlagCtrl = MCLocator(12, 16)

MCLType = MCLocator(16, 18)
MCLJmpCmpReg = MCLocator(18, 20)
MCLJmpCmpBit = MCLocator(20, 28)
MCLJmpCmpVal = MCLocator(28, 29)
MCLJmpTarget = MCLocator(29, 40)

""" ALU """
# MC_ALU_CTRL_SZ = 4
# assert len(ALUCtrl) < (1 << MC_ALU_CTRL_SZ)
#
# MC_ALU_CTRL_PORT_SZ = 4
# assert len(ALUPortCtrl) - 1 == MC_ALU_CTRL_PORT_SZ

""" Base """


class MCType(IntEnum):
    MC_RUN = 0b0
    MC_JMP = 0b1


class MCRegId(IntEnum):
    MC_R_PS = 0b0
    MC_R_CR = 0b1
