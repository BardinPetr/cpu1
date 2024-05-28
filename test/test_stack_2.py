import random

from myhdl import *

from machine.config import DATA_BITS
from machine.utils.hdl import Bus, Bus1
from src.machine.components import Clock
from src.machine.components import ExtendedStack
from src.machine.utils.introspection import introspect, IntrospectionTree
from src.machine.utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_stack_2():
    clk = Bus1()
    cld = Clock(clk, 10)

    DEPTH = 10

    in_data, out_tos0, out_tos1 = [Bus(bits=DATA_BITS) for _ in range(3)]
    out_full, out_empty, in_wr = Bus1(0), Bus1(1), Bus1(0)
    in_shift = Bus(min=-1, max=2)

    st = ExtendedStack(
        clk,
        in_shift, in_wr, in_data,
        out_tos0, out_tos1,
        out_empty, out_full,
        DEPTH
    )

    introspect()
    intro = IntrospectionTree.build(st)
    mem = intro.mem
    sp_intro = intro.sp

    def push(x):
        yield clk.posedge
        in_data.next = x
        in_shift.next = 1
        in_wr.next = 1
        yield clk.negedge
        yield delay(1)
        in_shift.next = 0
        in_wr.next = 0
        yield delay(1)

    def pop():
        yield clk.posedge
        in_shift.next = -1
        yield clk.negedge
        yield delay(1)
        in_shift.next = 0
        yield delay(1)

    @instance
    def stimulus():
        STACK = [0 for _ in range(DEPTH)]
        sp = 0

        for _ in range(2):
            DATA = [random.randrange(0, 1 << DATA_BITS - 1) for _ in range(DEPTH + 2)]

            # test push
            for i, v in enumerate(DATA):
                yield push(v)

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

            # test pop
            in_data.next = 0
            in_wr.next = 0
            for i in range(DEPTH + 2):
                yield pop()

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

        test_val = 0xDEAD
        test_val1 = 0xDDDD
        test_val2 = 0xABCD
        test_val3 = 0xBADC

        yield push(test_val1)
        yield push(test_val)

        assert mem[:2] == [test_val1, test_val]
        assert sp_intro == 2

        # test replace top
        yield clk.posedge
        in_data.next = test_val2
        in_shift.next = 0
        in_wr.next = 1
        yield clk.negedge
        yield delay(1)
        in_wr.next = 0
        yield delay(1)

        assert mem[:2] == [test_val1, test_val2]
        assert sp_intro == 2

        # test pop and replace
        yield clk.posedge
        in_data.next = test_val3
        in_shift.next = -1
        in_wr.next = 1
        yield clk.negedge
        yield delay(1)
        in_wr.next = 0
        yield delay(1)

        assert mem[0] == test_val3
        assert sp_intro == 1

        raise StopSimulation

    return introspect()
