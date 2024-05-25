import enum
import inspect
from enum import auto
from typing import Union, Dict

from src.machine.utils.enums import CEnumM, CEnumS, CtrlEnum


class PSFlags(CEnumM):
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


class RegFileIdCtrl(CEnumS):
    R0 = 0
    IP = 1
    CR = 2
    R1 = 3
    R2 = 4


class BusInCtrl(CEnumS):
    """
    Format:
    0xxx - xx is classic source
    1xxx - xx is regfile ID

    Currently free:
    0011
    011x
    11xx
    """
    Z = 0
    PS = 0b0001
    DR = 0b0010
    # 0011
    DST = 0b0100
    DSS = 0b0101
    RST = 0b0110
    RSS = 0b0111
    XX = 0b1000 + RegFileIdCtrl.R0
    IP = 0b1000 + RegFileIdCtrl.IP
    CR = 0b1000 + RegFileIdCtrl.CR
    YY = 0b1000 + RegFileIdCtrl.R1


class BusOutCtrl(CEnumS):
    """
    Format:
    00xx - xx is classic source
    10xx - xx is regfile ID
    """
    Z = 0b0000
    PS = 0b0001
    DR = 0b0010
    AR = 0b0011
    DS = 0b0100
    RS = 0b0101
    # 0110 0111
    R0 = 0b1000 + RegFileIdCtrl.R0
    IP = 0b1000 + RegFileIdCtrl.IP
    CR = 0b1000 + RegFileIdCtrl.CR
    R1 = 0b1000 + RegFileIdCtrl.R1
    R2 = 0b1000 + RegFileIdCtrl.R2


class RegFileOrNormalRegister(CEnumS):
    NR = 0
    RF = 1


class MemCtrl(CEnumS):
    IGN = 0
    WR = 1


class ALUCtrl(CEnumS):
    ZERO = 0
    PASSA = auto()
    AND = auto()
    OR = auto()
    ADD = auto()
    ADC = auto()
    MUL = auto()
    MOD = auto()
    DIV = auto()
    SHL = auto()
    SHR = auto()
    ASL = auto()
    ASR = auto()
    ROL = auto()
    ROR = auto()


class ALUPortCtrl(CEnumM):
    PASS = 0b0000
    NOT = 0b0001
    INC = 0b0010
    SXTB = 0b0100
    SXTW = 0b1000
    TKB = 0b10000
    TKW = 0b100000


class ALUFlagCtrl(CEnumM):
    SETZ = 1 << PSFlags.Z
    SETN = 1 << PSFlags.N
    SETC = 1 << PSFlags.C
    SETV = 1 << PSFlags.V


class StackCtrl(CEnumS):
    NONE = 0b000
    PUSH = 0b101
    POP = 0b011
    REP = 0b100
    POPREP = 0b111


def extract_enums() -> Dict[str, Dict[str, int]]:
    external_frame = inspect.getouterframes(inspect.currentframe())[1]
    f_locals = external_frame.frame.f_locals
    return {
        k: {e(e_k).name: e_k.value for e_k in e}
        for k, e in f_locals.items()
        if type(e) == enum.EnumType and issubclass(e, CtrlEnum) and len(e) > 0
    }
