from myhdl import *

from src.machine.arch import PSFlags, ALUCtrl, ALUPortCtrl
from src.machine.config import DATA_BITS
from src.machine.utils.hdl import hdl_block, dim
from src.machine.utils.introspection import introspect


def alu_apply_port(port_data: intbv, port_ctrl):
    res = intbv(port_data)[:]
    if int(port_ctrl) & ALUPortCtrl.TKB:
        res[:] = res[8:]
    elif int(port_ctrl) & ALUPortCtrl.TKW:
        res[:] = res[16:]

    if int(port_ctrl) & ALUPortCtrl.SXTB:
        res[32:8] = ((1 << 24) - 1) if res[7] else 0
    elif int(port_ctrl) & ALUPortCtrl.SXTW:
        res[32:16] = ((1 << 16) - 1) if res[15] else 0

    if int(port_ctrl) & ALUPortCtrl.NOT:
        res[32:] = ~res[32:]
    if int(port_ctrl) & ALUPortCtrl.INC:
        res[32:] = intbv(res + 1)[32:]

    return res


@hdl_block
def ALU(operation, porta_ctrl, portb_ctrl, in_a, in_b, out, flags_out):
    """
    Asynchronous 2-port ALU with operations from ALUCtrl enum.
    Each port has individual ALU_PORT_CTRL operations applied to it before main operation.
    :param operation:   main opearation from ALUCtrl
    :param porta_ctrl:  input port 1 pre-operation from  ALU_PORT_CTRL
    :param portb_ctrl:  input port 2 pre-operation from  ALU_PORT_CTRL
    :param in_a:        input signal for port A
    :param in_b:        input signal for port B
    :param out:         output signal.
    :param flags_out:
    """

    sz = dim(in_a)
    assert sz == dim(in_b)
    assert sz == dim(out)

    @always_comb
    def run():
        op_a = intbv(alu_apply_port(in_a.val, porta_ctrl))[DATA_BITS + 1 :]
        op_b = intbv(alu_apply_port(in_b.val, portb_ctrl))[DATA_BITS + 1 :]

        res = intbv(0)[DATA_BITS + 1 :]
        match operation:
            case ALUCtrl.ZERO:
                res[:] = 0
            case ALUCtrl.PASSA:
                res[:] = op_a
            case ALUCtrl.AND:
                res[:] = op_a & op_b
            case ALUCtrl.OR:
                res[:] = op_a | op_b
            case ALUCtrl.MUL:
                res[:] = op_a * op_b
            case ALUCtrl.MOD:
                if op_b != 0:
                    res[:] = op_a % op_b
            case ALUCtrl.DIV:
                if op_b != 0:
                    res[:] = op_a // op_b
            case ALUCtrl.ADD:
                res[:] = op_a + op_b
            case ALUCtrl.SHL:
                res[:] = (op_a << op_b)[sz:]
            case ALUCtrl.SHR:
                res[:] = op_a >> op_b

        out.next = res[DATA_BITS:]

        a_sign, b_sign, out_sign = (
            op_a[DATA_BITS - 1],
            op_b[DATA_BITS - 1],
            res[DATA_BITS - 1],
        )

        tmp_flags = intbv(0)[4:]
        tmp_flags[PSFlags.Z] = not res[DATA_BITS:]
        tmp_flags[PSFlags.N] = out_sign
        tmp_flags[PSFlags.C] = res[DATA_BITS]
        tmp_flags[PSFlags.V] = (a_sign ^ out_sign) & (a_sign ^ out_sign)
        flags_out.next = tmp_flags

    return introspect()
