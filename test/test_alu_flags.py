from random import randrange

from myhdl import *

from src.machine.arch import PSFlags, ALUCtrl, ALUPortCtrl
from src.machine.components.ALU import ALU
from src.machine.utils.hdl import *
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger
from src.machine.utils.testutils import myhdl_pytest

L = get_logger()

APC = ALUPortCtrl


@myhdl_pytest(gui=False)
def test_alu_flags():
    in_a, in_b = Bus(DIM), Bus(DIM)
    out = Bus(DIM)

    ctrl = Signal(ALUCtrl.ZERO)
    ctrla = Signal(APC.PASS)
    ctrlb = Signal(APC.PASS)
    flag_out = Bus(4)

    alu = ALU(ctrl, ctrla, ctrlb, in_a, in_b, out, flag_out)

    def call_alu(a, b=0, cin=0, mode=ALUCtrl.ADD):
        ctrl.next = mode
        ctrla.next = APC.PASS
        ctrlb.next = APC.PASS
        set_signed(in_a, a)
        set_signed(in_b, b)

    TESTS = [
        # zero flag
        (dict(a=0), dict(Z=1)),
        (dict(a=randrange(10, 10000)), dict(Z=0)),
        # negative flag
        *[(dict(a=randrange(10, 10000)), dict(Z=0, N=0, C=0)) for _ in range(10)],
        *[(dict(a=-randrange(10, 10000)), dict(Z=0, N=1, C=0)) for _ in range(10)],
        # unsigned overflow
        (dict(a=UINT_MAX), dict(C=0)),
        (dict(mode=ALUCtrl.ADD, a=UINT_MAX, b=1), dict(C=1)),
        # (dict(mode=ALUCtrl.ADC, cin=1, a=UINT_MAX, b=0), dict(C=1)),
        *[
            (
                dict(
                    mode=ALUCtrl.ADD,
                    a=UINT_MAX - randrange(1000, UINT_MAX // 2),
                    b=randrange(UINT_MAX // 2 + 1, UINT_MAX),
                ),
                dict(C=1),
            )
            for _ in range(10)
        ],
        # signed overflow
        (dict(a=SINT_MAX), dict(V=0)),
        (dict(a=SINT_MIN), dict(V=0)),
        (dict(mode=ALUCtrl.ADD, a=SINT_MAX, b=1), dict(V=1)),
        (dict(mode=ALUCtrl.ADD, a=SINT_MIN, b=negate(1)), dict(V=1)),
        (dict(mode=ALUCtrl.ADD, a=SINT_MAX, b=negate(1)), dict(V=0)),
        (dict(mode=ALUCtrl.ADD, a=SINT_MIN, b=1), dict(V=0)),
        *[
            (
                dict(
                    mode=ALUCtrl.ADD,
                    a=SINT_MAX - randrange(1000, SINT_MAX // 2),
                    b=randrange(SINT_MAX // 2 + 10, SINT_MAX),
                ),
                dict(V=1),
            )
            for _ in range(10)
        ],
        *[
            (
                dict(
                    mode=ALUCtrl.ADD,
                    a=SINT_MIN + randrange(1000, SINT_MAX // 2),
                    b=negate(randrange(SINT_MAX // 2 + 10, SINT_MAX)),
                ),
                dict(V=1),
            )
            for _ in range(10)
        ],
        # signed overflow with carry addition
        # (dict(mode=ALUCtrl.ADC, a=SINT_MAX, b=0, cin=1), dict(V=1)),
        # (dict(mode=ALUCtrl.ADC, a=SINT_MAX, b=negate(1), cin=1), dict(V=0)),
        # (dict(mode=ALUCtrl.ADC, a=SINT_MIN, b=negate(1), cin=1), dict(V=0)),
        # (dict(mode=ALUCtrl.ADC, a=SINT_MIN, b=negate(2), cin=1), dict(V=1)),
    ]

    print()

    @instance
    def stimulus():
        for test, flags in TESTS:
            call_alu(**test)
            yield delay(1)

            real_flags = PSFlags.decode_flags(flag_out)

            L.debug(
                f"Got flags: {PSFlags.print_flags(flag_out)}; Valid: {flags}; Test was: {test}"
            )

            for flag, val in flags.items():
                assert real_flags[flag] == val

        raise StopSimulation

    return introspect()
