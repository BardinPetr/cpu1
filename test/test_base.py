import random

from myhdl import *

from src.components.base import Clock, Trig, RTrig, Counter
from utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_base_trig():
    clk = Signal(False)
    cld = Clock(clk, 10)

    d_in, d_out1, d_out2 = [Signal(intbv(0)[:8]) for _ in range(3)]
    rst = ResetSignal(False, active=True, isasync=True)

    trig = Trig(d_in, d_out1, clk)
    rtrig = RTrig(d_in, d_out2, clk, rst)

    @instance
    def stimulus():
        r_test = 5
        for i in range(10):
            yield clk.negedge

            val = random.randrange(2 ** 8)
            d_in.next = val

            if i == r_test:
                rst.next = True

            yield clk.posedge
            yield delay(5)

            rst.next = False

            assert d_out1.val == val
            assert d_out2.val == (val if i != r_test else 0)

        raise StopSimulation

    return instances()


@myhdl_pytest(gui=False)
def test_base_counter():
    clk = Signal(False)
    cld = Clock(clk, 10)

    rst = ResetSignal(False, active=True, isasync=True)

    MAX = 1 << 4
    val = Signal(intbv(0, 0, MAX + 1))

    cntr = Counter(clk, rst, val)

    @instance
    def stimulus():
        for i in range(1, MAX):
            yield clk.negedge
            assert val.val == i

        rst.next = True
        yield clk.negedge
        rst.next = False
        assert val.val == 0

        for i in range(1, MAX // 2):
            yield clk.negedge
            assert val.val == i

        raise StopSimulation

    return instances()
