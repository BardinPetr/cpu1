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

from enum import IntEnum, Enum
from math import ceil, log2
from typing import TypeVar, Optional, Sized

from myhdl import intbv

from src.arch import BusInCtrl, BusOutCtrl, MemCtrl
from src.components.ALU import ALUCtrl, ALUPortCtrl, ALUFlagCtrl

T = TypeVar('T', bound=IntEnum)


class MCType(IntEnum):
    MC_RUN = 0b0
    MC_JMP = 0b1


class MCSelectType(Enum):
    SINGLE = 0
    MULTIPLE = 1
    AS_IS = MULTIPLE


class MCLocator:
    _cur_pos = 0

    def __init__(self, select=MCSelectType.SINGLE, content: Optional[Sized] = None, bits: Optional[int] = None):
        self.loc_start = 0
        self.select = select

        if bits is None:
            assert content is not None, "No way to deduce partial locator size"
            sz = len(content)
            if select == MCSelectType.SINGLE:
                bits = ceil(log2(max(2, sz)))
            else:
                bits = max(1, sz)
        self.size = bits

    @property
    def loc_end(self):
        return self.loc_start + self.size

    def put(self, target: intbv, source):
        target[self.loc_end:self.loc_start] = source

    def get(self, source: intbv) -> intbv:
        return source[self.loc_end:self.loc_start]

    def at(self, pos: int) -> 'MCLocator':
        self.loc_start = pos
        return self

    def after(self, prev: 'MCLocator') -> 'MCLocator':
        self.loc_start = prev.loc_end
        return self

    @staticmethod
    def single(content: Optional[Sized] = None, bits: Optional[int] = None):
        return MCLocator(MCSelectType.SINGLE, content, bits)

    @staticmethod
    def multiple(content: Optional[Sized] = None, bits: Optional[int] = None):
        return MCLocator(MCSelectType.MULTIPLE, content, bits)


LCSIN, LCMUL = MCLocator.single, MCLocator.multiple

MCALUCtrl = LCSIN(ALUCtrl).at(0)
MCALUPortACtrl = LCMUL(ALUPortCtrl).after(MCALUCtrl)
MCALUPortBCtrl = LCMUL(ALUPortCtrl).after(MCALUPortACtrl)
MCALUFlagCtrl = LCMUL(ALUFlagCtrl).after(MCALUPortBCtrl)
MCBusACtrl = LCSIN(BusInCtrl).after(MCALUFlagCtrl)
MCBusBCtrl = LCSIN(BusInCtrl).after(MCBusACtrl)
MCBusCCtrl = LCSIN(BusOutCtrl).after(MCBusBCtrl)
MCMemCtrl = LCMUL(MemCtrl).after(MCBusCCtrl)

MCLJmpCmpBit = LCSIN(bits=16).after(MCBusCCtrl)
MCLJmpCmpVal = MCLocator(MCSelectType.AS_IS, bits=1).after(MCLJmpCmpBit)
MCLJmpTarget = MCLocator(MCSelectType.AS_IS, bits=11).after(MCLJmpCmpVal)

MCLType = LCSIN(MCType).after(MCLJmpTarget)

print(f"MC LEN={MCLType.loc_end}")
