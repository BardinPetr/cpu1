"""
CMD


JMP
24:23  23:11    11:10   10:2    2:0
typ    target   cmp_val cmp_bit cmp_reg



"""
from enum import IntEnum

from myhdl import intbv


class MCType(IntEnum):
    MC_RUN = 0b0
    MC_JMP = 0b1


class MCRegId(IntEnum):
    MC_R_PS = 0b0
    MC_R_CR = 0b1


class MCALUCtrl(IntEnum):
    pass


class MCALUPortCtrl(IntEnum):
    pass


def mc_get_cmp_reg(mc: intbv) -> intbv:
    return mc[2:0]


def mc_get_cmp_bit(mc: intbv) -> intbv:
    return mc[10:2]


def mc_get_cmp_val(mc: intbv) -> intbv:
    return mc[11:10]


def mc_get_cmp_jmp(mc: intbv) -> intbv:
    return mc[19:11]


def mc_get_type(mc: intbv) -> intbv:
    return mc[20:19]
