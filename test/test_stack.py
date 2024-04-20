import random

from myhdl import *

from machine.arch import StackCtrl
from machine.components.Stack import Stack
from machine.components.base import Clock, Trig, RTrig, Counter
from machine.config import DATA_BITS
from machine.utils.hdl import Bus1, Bus
from machine.utils.introspection import introspect, IntrospectionTree
from machine.utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_stack():
    clk = Bus1()
    cld = Clock(clk, 10)

    DEPTH = 10

    in_data, out_tos0, out_tos1 = [Bus(bits=DATA_BITS) for _ in range(3)]
    out_full, out_empty = Bus1(0), Bus1(1)
    in_ctrl = Bus(enum=StackCtrl)
    st = Stack(
        clk,
        in_ctrl, in_data,
        out_tos0, out_tos1,
        out_empty, out_full,
        DEPTH
    )

    introspect()
    intro = IntrospectionTree.build(st)
    mem = intro.mem

    @instance
    def stimulus():
        STACK = [0 for _ in range(DEPTH)]
        sp = 0

        for _ in range(2):
            DATA = [random.randrange(0, 1 << DATA_BITS - 1) for _ in range(DEPTH + 1)]

            for i, v in enumerate(DATA):
                yield clk.posedge
                in_data.next = v
                in_ctrl.next = StackCtrl.PUSH
                yield clk.negedge
                in_ctrl.next = StackCtrl.NONE
                yield delay(1)

                if i < DEPTH:
                    STACK[sp] = v
                assert STACK == mem[:]

                assert out_empty == 0

                if i >= DEPTH - 1:
                    assert out_full == 1
                    assert out_tos0 == DATA[DEPTH - 1]
                    assert out_tos1 == DATA[DEPTH - 2]
                else:
                    sp += 1
                    assert out_full == 0

                    assert out_tos0 == DATA[sp - 1]
                    if i == 0:
                        assert out_tos1 == 0
                    else:
                        assert out_tos1 == DATA[sp - 2]

            in_data.next = 0

            for i in range(DEPTH + 1):
                yield clk.posedge
                in_ctrl.next = StackCtrl.POP
                yield clk.negedge
                in_ctrl.next = StackCtrl.NONE
                yield delay(1)

                assert out_full == 0

                if i >= (DEPTH - 1):
                    assert out_empty == 1
                    assert out_tos0 == 0
                    assert out_tos1 == 0
                else:
                    sp -= 1
                    assert out_empty == 0
                    assert out_tos0 == DATA[DEPTH - i - 2]
                    if (DEPTH - i - 3) < 0:
                        assert out_tos1 == 0
                    else:
                        assert out_tos1 == DATA[DEPTH - i - 3]

        raise StopSimulation

    return introspect()
