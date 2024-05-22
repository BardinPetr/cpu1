import random

from myhdl import *

from src.machine.arch import ALUPortCtrl, ALUCtrl, PSFlags
from src.machine.components.ALU import ALU
from src.machine.config import DATA_BITS
from src.machine.utils.hdl import Bus
from src.machine.utils.introspection import introspect
from src.machine.utils.testutils import myhdl_pytest

DIM = DATA_BITS
UMAX = (1 << DIM) - 1
SMAX = (1 << (DIM - 1)) - 1

APC = ALUPortCtrl


def trunc(x, n=DIM):
    return x & ((1 << n) - 1)


TEST_FUNCS = {
    # basic
    'ZERO':   lambda a, b, c: (ALUCtrl.ZERO, APC.PASS, APC.PASS, 0),
    # logic
    'OR':     lambda a, b, c: (ALUCtrl.OR, APC.PASS, APC.PASS, a | b),
    'AND':    lambda a, b, c: (ALUCtrl.AND, APC.PASS, APC.PASS, a & b),
    # check inversion on both ports
    'ANDNN':  lambda a, b, c: (ALUCtrl.AND, APC.NOT, APC.NOT, trunc(~(a | b))),
    # addition
    'ADD':    lambda a, b, c: (ALUCtrl.ADD, APC.PASS, APC.PASS, trunc(a + b)),
    'ADC':    lambda a, b, c: (ALUCtrl.ADC, APC.PASS, APC.PASS, trunc(a + b + c)),
    # check negation (subtraction via addition)
    'SUB':    lambda a, b, c: (ALUCtrl.ADD, APC.PASS, APC.NOT | APC.INC, trunc(a - b)),
    'SUBREV': lambda a, b, c: (ALUCtrl.ADD, APC.NOT | APC.INC, APC.PASS, trunc(b - a)),
    # check addition of 8bit sign extended value to normal
    'ADDM8':  lambda a, b, c: (ALUCtrl.ADD, APC.PASS, APC.SXTB, trunc(a - (trunc(~b + 1, 8) if b & (1 << 7) else -b))),
    # logic shifts
    'SHL':    lambda a, b, c: (ALUCtrl.SHL, APC.PASS, APC.PASS, trunc(a << b)),
    'SHR':    lambda a, b, c: (ALUCtrl.SHR, APC.PASS, APC.PASS, trunc(a >> b)),
}


@myhdl_pytest(gui=False)
def test_alu():
    in_a, in_b = Bus(DIM), Bus(DIM)
    out = Bus(DIM)

    ctrl = Signal(ALUCtrl.ZERO)
    ctrla = Signal(APC.PASS)
    ctrlb = Signal(APC.PASS)
    flag_ctrl = Bus(4, state=0b1111)
    flag_in = Bus(4)
    flag_out = Bus(4)

    alu = ALU(ctrl, ctrla, ctrlb, in_a, in_b, out, flag_ctrl, flag_in, flag_out)

    # alu.convert('Verilog')

    def call_alu(c, ca, cb, a, b, cin) -> int:
        ctrl.next = c
        ctrla.next = ca
        ctrlb.next = cb
        if a < 0:
            in_a.next.signed = a
        else:
            in_a.next = a
        if b < 0:
            in_b.next.signed = b
        else:
            in_b.next = b
        flag_in.next = (cin << PSFlags.C)

    LARGE = [random.randrange(1 << 31, 1 << 32) for _ in range(2)]

    CHECKS = [
        ('ZERO', 123, 321, 0),
        *[('AND', None, None, 0)] * 10,
        *[('OR', None, None, 0)] * 10,
        *[('ANDNN', None, None, 0)] * 2,
        ('ADD', (1 << 32) - 1, None, 0),
        ('ADD', LARGE[0], LARGE[1], 0),
        *[('ADD', None, None, 0)] * 10,
        ('ADC', LARGE[0], LARGE[1], 0),
        ('ADC', LARGE[0], LARGE[1], 1),
        ('SUB', max(LARGE), min(LARGE), 0),
        ('SUB', min(LARGE), max(LARGE), 0),
        *[('SUB', None, None, 0)] * 10,
        *[('SUBREV', None, None, 0)] * 10,
        ('ADDM8', None, 0b11001101, 0),
        ('ADDM8', None, 0b11111000, 0),
        ('ADDM8', None, 0b00011111, 0),
        ('ADDM8', None, 0b01010111, 0),
        *[('SHL', None, i, 0) for i in range(0, DIM + 3, 3)],
        *[('SHR', None, i, 0) for i in range(0, DIM + 3, 3)],
    ]

    @instance
    def stimulus():
        for t_func, t_a, t_b, t_cin in CHECKS:
            if t_a is None:
                t_a = random.randrange(1 << 2, 1 << 32)
            if t_b is None:
                t_b = random.randrange(1 << 2, 1 << 32)

            t_ctrl, t_cpa, t_cpb, chk_out = TEST_FUNCS[t_func](t_a, t_b, t_cin)

            call_alu(
                t_ctrl,
                t_cpa, t_cpb,
                t_a, t_b,
                t_cin
            )
            yield delay(1)

            # print(f"{t_func} A=0x{t_a:08x} B=0x{t_b:08x} -> real=0x{int(out.val):08x} required=0x{int(chk_out):08x}")
            assert out.val == chk_out

        raise StopSimulation

    return introspect()
