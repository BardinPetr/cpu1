from enum import IntEnum
from math import ceil, log2
from typing import TypeVar, Optional, Sized, Union

from myhdl import intbv

from machine.arch import BusInCtrl, BusOutCtrl, MemCtrl, ALUCtrl, ALUPortCtrl, ALUFlagCtrl, StackCtrl
from machine.utils.enums import CtrlEnum, EnumEncodingType, EncodedEnum

T = TypeVar('T', bound=IntEnum)


class MCType(IntEnum):
    MC_RUN = 0b0
    MC_JMP = 0b1


class MCLocator:
    def __init__(self,
                 content: Optional[Sized | CtrlEnum] = None,
                 bits: Optional[int] = None,
                 select=EnumEncodingType.AS_IS):
        if bits is None:
            assert content is not None, "No way to deduce partial locator size"

            if issubclass(content, CtrlEnum):
                select = content.encoding_type()
                bits = content.encoded_len()
            else:
                sz = len(content)
                if select == EnumEncodingType.SINGLE:
                    bits = ceil(log2(max(2, sz)))
                else:
                    bits = max(1, sz)

        self.size = bits
        self.select = select
        self.loc_start = 0

    @property
    def loc_end(self):
        return self.loc_start + self.size

    def put(self, target: intbv, source: Union[int, intbv, EncodedEnum]):
        if isinstance(source, EncodedEnum):
            source = source.value
        target[self.loc_end:self.loc_start] = source

    def get(self, source: intbv) -> intbv:
        return source[self.loc_end:self.loc_start]

    def at(self, pos: int) -> 'MCLocator':
        self.loc_start = pos
        return self

    def after(self, prev: 'MCLocator') -> 'MCLocator':
        self.loc_start = prev.loc_end
        return self


L = MCLocator

# common
MCLType = L(MCType).at(0)
MCALUCtrl = L(ALUCtrl).after(MCLType)
MCALUPortACtrl = L(ALUPortCtrl).after(MCALUCtrl)
MCALUPortBCtrl = L(ALUPortCtrl).after(MCALUPortACtrl)
MCBusACtrl = L(BusInCtrl).after(MCALUPortBCtrl)
MCBusBCtrl = L(BusInCtrl).after(MCBusACtrl)

# ending for operational
MCALUFlagCtrl = L(ALUFlagCtrl).after(MCBusBCtrl)
MCBusCCtrl = L(BusOutCtrl).after(MCALUFlagCtrl)
MCMemCtrl = L(MemCtrl).after(MCBusCCtrl)
MCStackDCtrl = L(StackCtrl).after(MCMemCtrl)
MCStackRCtrl = L(StackCtrl).after(MCStackDCtrl)

# ending for
MCJmpCmpBit = L(bits=16).after(MCBusBCtrl)
MCJmpCmpVal = L(bits=1).after(MCJmpCmpBit)
MCJmpTarget = L(bits=11).after(MCJmpCmpVal)

MCHeadNormal = MCStackRCtrl
MCHeadJump = MCJmpTarget

if __name__ == "__main__":
    print(f"MCN LEN={MCHeadNormal.loc_end}")
    print(f"MCJ LEN={MCHeadJump.loc_end}")
