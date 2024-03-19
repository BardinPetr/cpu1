from random import randint

from myhdl import *

from src.components.ALU import ALU, ALU_CTRL, ALU_PORT_CTRL
from utils.hdl import Bus
from utils.testutils import myhdl_pytest

TEST_FUNCS = {
    ALU_CTRL.ZERO:  lambda a, b: 0,
    ALU_CTRL.PASSA: lambda a, b: a,
    ALU_CTRL.PASSB: lambda a, b: b,
    ALU_CTRL.ADD:   lambda a, b: (a + b) % 256,
    # ALU_CTRL.ADC:   lambda a, b:,
    ALU_CTRL.SUB:   lambda a, b: a - b,
    # ALU_CTRL.MUL:   lambda a, b: a * b,
    ALU_CTRL.DIV:   lambda a, b: a // b,
    ALU_CTRL.MOD:   lambda a, b: a % b,
    # ALU_CTRL.SHL:   lambda a, b: a << b,
    # ALU_CTRL.SHR:   lambda a, b: a >> b,
    # ALU_CTRL.ROL:   lambda a, b:,
    # ALU_CTRL.ROR:   lambda a, b:
}


@myhdl_pytest(gui=True)
def test_alu():
    DIM = 8

    in_a, in_b = Bus(DIM), Bus(DIM)
    out = Bus(DIM + 1)

    in_carry = Signal(False)
    ctrl = Signal(ALU_CTRL.ZERO)
    ctrla = Signal(ALU_PORT_CTRL.INV)
    ctrlb = Signal(ALU_PORT_CTRL.PASS)

    alu = ALU(ctrl, ctrla, ctrlb, in_a, in_b, out, in_carry)
    alu.convert('Verilog')

    def call_alu(c, ca, cb, a, b) -> int:
        ctrl.next = c
        ctrla.next = ca
        ctrlb.next = cb
        in_a.next = a
        in_b.next = b

    @instance
    def stimulus():
        for t_ctrl, t_checker in TEST_FUNCS.items():
            a, b = [randint(0, 1 << DIM) for _ in range(2)]
            b, a = max(a, b), min(a, b)
            call_alu(t_ctrl, ALU_PORT_CTRL.PASS, ALU_PORT_CTRL.PASS, a, b)
            yield delay(1)
            res = int(out.val)
            print(f"{t_ctrl}({a=}, {b=})={res}; should be {t_checker(a, b)}")
            # assert t_checker(a, b) == res
            yield delay(1)

        raise StopSimulation

    return alu, stimulus
