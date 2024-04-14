from enum import IntEnum, auto

from myhdl import *

from src.arch import PSFlags
from src.config import DATA_BITS, REG_PS_SZ
from utils.enums import EnumEncoding, EnumSC, EnumMC
from utils.hdl import hdl_block, dim
from utils.introspection import introspect


class ALUCtrl(EnumSC):
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


class ALUPortCtrl(EnumMC):
    PASS = 0b0000
    NOT = 0b0001
    INC = 0b0010
    SXT8 = 0b0100
    SXT16 = 0b1000


class ALUFlagCtrl(EnumMC):
    SETZ = 1 << PSFlags.Z
    SETN = 1 << PSFlags.N
    SETV = 1 << PSFlags.V
    SETC = 1 << PSFlags.C


def alu_apply_port(port_data: intbv, port_ctrl):
    res = intbv(port_data)
    if int(port_ctrl) & ALUPortCtrl.NOT:
        res[:] = ~res
    if int(port_ctrl) & ALUPortCtrl.INC:
        res[:] = res + 1
    if int(port_ctrl) & ALUPortCtrl.SXT8:
        res[32:8] = ((1 << 24) - 1) if res[7] else 0
    if int(port_ctrl) & ALUPortCtrl.SXT16:
        res[32:16] = ((1 << 16) - 1) if res[15] else 0
    return res


@hdl_block
def ALU(operation,
        porta_ctrl, portb_ctrl,
        in_a, in_b,
        out,
        flag_ctrl,
        flags_in, flags_out):
    """
    Asynchronous 2-port ALU with operations from ALUCtrl enum.
    Each port has individual ALU_PORT_CTRL operations applied to it before main operation.
    :param operation:   main opearation from ALUCtrl
    :param porta_ctrl:  input port 1 pre-operation from  ALU_PORT_CTRL
    :param portb_ctrl:  input port 2 pre-operation from  ALU_PORT_CTRL
    :param in_a:        input signal for port A
    :param in_b:        input signal for port B
    :param out:         output signal.
    :param flag_ctrl:
    :param flags_in:
    :param flags_out:
    """

    sz = dim(in_a)
    assert sz == dim(in_b)
    assert sz == dim(out)

    tmp_flags = intbv(0)[REG_PS_SZ:]

    @always_comb
    def run():
        op_a = alu_apply_port(in_a.val, porta_ctrl)
        op_b = alu_apply_port(in_b.val, portb_ctrl)

        res = intbv(0)[DATA_BITS + 1:]
        match operation:
            case ALUCtrl.ZERO:
                res[:] = 0
            case ALUCtrl.PASSA:
                res[:] = op_a
            case ALUCtrl.PASSB:
                res[:] = op_b
            case ALUCtrl.AND:
                res[:] = op_a & op_b
            case ALUCtrl.OR:
                res[:] = op_a | op_b
            case ALUCtrl.ADD:
                res[:] = op_a + op_b
            case ALUCtrl.ADC:
                res[:] = op_a + op_b + flags_in[PSFlags.C]
            case ALUCtrl.SHL:
                res[:] = (op_a << op_b)[sz:]
            case ALUCtrl.SHR:
                res[:] = op_a >> op_b
            case ALUCtrl.ASL:
                raise Exception("Not implemented")
            case ALUCtrl.ASR:
                raise Exception("Not implemented")
            case ALUCtrl.ROL:
                raise Exception("Not implemented")
            case ALUCtrl.ROR:
                raise Exception("Not implemented")

        out.next = res[DATA_BITS:]

        tmp_flags[:] = flags_in.val

        if flag_ctrl.val & ALUFlagCtrl.SETZ:
            tmp_flags[PSFlags.Z] = not res
        if flag_ctrl.val & ALUFlagCtrl.SETN:
            tmp_flags[PSFlags.N] = res[DATA_BITS - 1]
        if flag_ctrl.val & ALUFlagCtrl.SETC:
            tmp_flags[PSFlags.C] = res[DATA_BITS]
        if flag_ctrl.val & ALUFlagCtrl.SETV:
            out_sign = res[DATA_BITS - 1]
            a_sign, b_sign = op_a[DATA_BITS - 1], op_b[DATA_BITS - 1]
            tmp_flags[PSFlags.V] = (out_sign ^ a_sign) & (out_sign ^ b_sign)

        flags_out.next = tmp_flags

    return introspect()
