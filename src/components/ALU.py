from myhdl import *
from myhdl import _Signal

from src.config import DATA_BITS
from utils.hdl import hdl_block, dim

ALU_CTRL = enum(
    'ZERO', 'PASSA', 'PASSB', 'ADD', 'ADC', 'SUB', 'MUL', 'DIV', 'MOD', 'SHL', 'SHR', 'ROL', 'ROR',
    encoding='binary'
)
ALU_PORT_CTRL = enum(
    'PASS', 'INC', 'INV', 'SXT', 'APPC', 'ADDC',
    encoding='one_hot'
)


def alu_apply_port(port_data: intbv, port_ctrl):
    res = intbv(port_data)
    if int(port_ctrl) & int(ALU_PORT_CTRL.INV):
        res[:] = ~res
    if int(port_ctrl) & int(ALU_PORT_CTRL.INC):
        res[:] = res + 1
    return res


@hdl_block
def ALU(operation: _Signal,
        porta_ctrl: _Signal, portb_ctrl: _Signal,
        in_a: _Signal, in_b: _Signal,
        out: _Signal,
        in_carry: _Signal):
    """
    Asynchronous 2-port ALU with operations from ALU_CTRL enum.
    Each port has individual ALU_PORT_CTRL operations applied to it before main operation.
    :param operation:   main opearation from ALU_CTRL
    :param porta_ctrl:  input port 1 pre-operation from  ALU_PORT_CTRL
    :param portb_ctrl:  input port 2 pre-operation from  ALU_PORT_CTRL
    :param in_a:        input signal for port A
    :param in_b:        input signal for port B
    :param out:         output signal. should have 1 bit more than input ports
    :param in_carry:    carry flag input
    """

    d = dim(in_a)
    assert d == dim(in_b)
    assert d == (dim(out) - 1)

    @always_comb
    def run():
        op_a = alu_apply_port(in_a.val, porta_ctrl)
        op_b = alu_apply_port(in_b.val, portb_ctrl)

        res = intbv()
        match operation:
            case ALU_CTRL.PASSA:
                res[:] = op_a
            case ALU_CTRL.PASSB:
                res[:] = op_b
            case ALU_CTRL.ADD:
                res[:] = op_a + op_b
            case ALU_CTRL.SUB:
                res[:] = op_a - op_b
            # case ALU_CTRL.ADC: # TODO
            #     res[:] = op_a + op_b + in_carry
            case ALU_CTRL.MUL:
                res[:] = op_a * op_b
            case ALU_CTRL.SHL:
                op_b[:] = min(op_b, intbv(d))
                res[:] = op_a << op_b
            case ALU_CTRL.SHR:
                op_b[:] = min(op_b, intbv(d))
                res[:] = op_a >> op_b
            # case ALU_CTRL.ROL:
            #     mov = int(op_b % (d + 1))
            #     res[mov - 1] = in_carry
            #     res[:mov] = op_a[(d - mov):]
            #     res[mov - 1:] = op_a[:(d - mov + 1)]
            # case ALU_CTRL.ROR:
            #     op_b[:] = op_b % (d + 1) # TODO

        # result may overflow original type size, so cut to output DATA_BITS and one bit for carry
        out.next = res[DATA_BITS + 1:]

    return run
