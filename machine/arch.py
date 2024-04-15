import enum
import inspect
from enum import auto
from typing import Union, Dict

from machine.utils.enums import CEnumM, CEnumS, CtrlEnum


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
    XX = 0
    IP = 1
    CR = 2
    YY = 3


class RegisterIdCtrl(CEnumS):
    CR = 0


class BusInCtrl(CEnumS):
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


class BusOutCtrl(CEnumS):
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


class RegFileOrNormalRegister(CEnumS):
    NR = 0
    RF = 1


class MemCtrl(CEnumS):
    IGN = 0
    WR = 1


class ALUCtrl(CEnumS):
    ZERO = 0
    PASSA = auto()
    PASSB = auto()
    AND = auto()
    OR = auto()
    ADD = auto()
    ADC = auto()
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
    SXT8 = 0b0100
    SXT16 = 0b1000


class ALUFlagCtrl(CEnumM):
    SETZ = 1 << PSFlags.Z
    SETN = 1 << PSFlags.N
    SETV = 1 << PSFlags.V
    SETC = 1 << PSFlags.C


def extract_enums() -> Dict[str, Dict[str, int]]:
    external_frame = inspect.getouterframes(inspect.currentframe())[1]
    f_locals = external_frame.frame.f_locals
    return {
        k: {e(e_k).name: e_k.value for e_k in e}
        for k, e in f_locals.items()
        if type(e) == enum.EnumType and issubclass(e, CtrlEnum) and len(e) > 0
    }