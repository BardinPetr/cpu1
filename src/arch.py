from enum import IntEnum
from typing import Union


class PSFlags(IntEnum):
    Z = 0
    N = 1
    C = 2
    V = 3
    RUN = 4
    INT = 5
    IEN = 6

    @staticmethod
    def decode_flags(val: Union['PSFlags', int]) -> dict:
        val = int(val)
        return {i.name: bool(val & (1 << i.value)) for i in PSFlags}

    @staticmethod
    def print_flags(val: Union['PSFlags', int]) -> str:
        decoded = PSFlags.decode_flags(val)
        decoded = sorted(decoded.items(), key=lambda x: -PSFlags[x[0]].value)
        return ''.join((n if v else '-') for n, v in decoded)


class RegFileIdCtrl(IntEnum):
    XX = 0
    IP = 1
    CR = 2
    YY = 3


class RegisterIdCtrl(IntEnum):
    CR = 0


class BusInCtrl(IntEnum):
    """
    Format:
    0xx - xx is classic source
    1xx - xx is regfile ID
    """
    IGNORE = 0b000
    PS = 0b001
    DRR = 0b010
    SRC_3 = 0b011
    RF_XX = 0b100 + RegFileIdCtrl.XX
    RF_IP = 0b100 + RegFileIdCtrl.IP
    RF_CR = 0b100 + RegFileIdCtrl.CR
    RF_YY = 0b100 + RegFileIdCtrl.YY


class BusOutCtrl(IntEnum):
    """
    Format:
    0xx - xx is classic source
    1xx - xx is regfile ID
    """
    IGNORE = 0b000
    PS = 0b001
    DRW = 0b010
    AR = 0b011
    RF_XX = 0b100 + RegFileIdCtrl.XX
    RF_IP = 0b100 + RegFileIdCtrl.IP
    RF_CR = 0b100 + RegFileIdCtrl.CR
    RF_YY = 0b100 + RegFileIdCtrl.YY


class MemCtrl(IntEnum):
    IGN = 0
    WR = 1
