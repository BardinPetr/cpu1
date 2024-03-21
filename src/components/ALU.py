from enum import IntEnum

from myhdl import *
from myhdl import _Signal

from src.arch import PSFlags
from src.config import DATA_BITS
from utils.hdl import hdl_block, dim, Bus

ALU_CTRL = enum(
    'ZERO', 'PASSA', 'PASSB', 'AND', 'OR', 'ADD', 'ADC', 'SHL', 'SHR', 'ASL', 'ASR', 'ROL', 'ROR',
    encoding='binary'
)


class ALUPortCtrl(IntEnum):
    PASS = 0b0000
    NOT = 0b0001
    INC = 0b0010
    SXT8 = 0b0100
    SXT16 = 0b1000


class ALUFlagControl(IntEnum):
    SETZ = 1
    SETN = 2
    SETV = 4
    SETC = 8


def alu_apply_port(port_data: intbv, port_ctrl):
    res = intbv(port_data)
    if int(port_ctrl) & ALUPortCtrl.NOT:
        res[:] = ~res
    if int(port_ctrl) & ALUPortCtrl.INC:
        res[:] = res + 1
    if int(port_ctrl) & ALUPortCtrl.SXT8:
        res[32:8] = ((1 << 24) - 1) if res[7] else 0
    if int(port_ctrl) & ALUPortCtrl.SXT16:
        res[32:16] = ((1 << 16) - 1) if res[7] else 0
    return res


@hdl_block
def ALU(operation: _Signal,
        porta_ctrl: _Signal, portb_ctrl: _Signal,
        in_a: _Signal, in_b: _Signal,
        out: _Signal,
        flag_ctrl: _Signal,
        flags_in: _Signal, flags_out: _Signal):
    """
    Asynchronous 2-port ALU with operations from ALU_CTRL enum.
    Each port has individual ALU_PORT_CTRL operations applied to it before main operation.
    :param operation:   main opearation from ALU_CTRL
    :param porta_ctrl:  input port 1 pre-operation from  ALU_PORT_CTRL
    :param portb_ctrl:  input port 2 pre-operation from  ALU_PORT_CTRL
    :param in_a:        input signal for port A
    :param in_b:        input signal for port B
    :param out:         output signal. should have 1 bit more than input ports
    """

    sz = dim(in_a)
    assert sz == dim(in_b)
    assert sz == dim(out)

    tmp_flags = intbv(0)[4:]
    flag_c = intbv(False)

    @always_comb
    def run():
        op_a = alu_apply_port(in_a.val, porta_ctrl)
        op_b = alu_apply_port(in_b.val, portb_ctrl)

        res = intbv(0)[DATA_BITS + 1:]
        match operation:
            case ALU_CTRL.ZERO:
                res[:] = 0
            case ALU_CTRL.PASSA:
                res[:] = op_a
            case ALU_CTRL.PASSB:
                res[:] = op_b
            case ALU_CTRL.AND:
                res[:] = op_a & op_b
            case ALU_CTRL.OR:
                res[:] = op_a | op_b
            case ALU_CTRL.ADD:
                res[:] = op_a + op_b
            case ALU_CTRL.ADC:
                res[:] = op_a + op_b + flags_in[PSFlags.C]
            case ALU_CTRL.SHL:
                res[:] = (op_a << op_b)[sz:]
            case ALU_CTRL.SHR:
                res[:] = op_a >> op_b
            case ALU_CTRL.ASL:
                raise Exception("Not implemented")
            case ALU_CTRL.ASR:
                raise Exception("Not implemented")
            case ALU_CTRL.ROL:
                raise Exception("Not implemented")
            case ALU_CTRL.ROR:
                raise Exception("Not implemented")

        out.next = res[DATA_BITS:]

        tmp_flags[:] = flags_in.val

        if flag_ctrl.val & ALUFlagControl.SETZ:
            tmp_flags[PSFlags.Z] = not res
        if flag_ctrl.val & ALUFlagControl.SETN:
            tmp_flags[PSFlags.N] = res[DATA_BITS]
        if flag_ctrl.val & ALUFlagControl.SETC:
            tmp_flags[PSFlags.C] = res[DATA_BITS]
        if flag_ctrl.val & ALUFlagControl.SETV:
            tmp_flags[PSFlags.V] = res[DATA_BITS] ^ flags_in[PSFlags.C]

        flags_out.next = tmp_flags

    return instances()
