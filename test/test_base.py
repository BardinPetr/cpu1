import random

from myhdl import *

from src.base import Mux, Clock, Trig, RTrig
from utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_base_mux():
    inputs = [Signal(intbv(i)[8:]) for i in range(32)]
    outputs = [Signal(intbv(0)[8:]) for i in range(2)]
    ctrls = [Signal(intbv(0)[8:]) for i in range(2)]

    m2 = Mux(inputs[:2], outputs[0], ctrls[0])
    m32 = Mux(inputs[:32], outputs[1], ctrls[1])

    @instance
    def stimulus():
        for i, dim in enumerate([1, 5]):
            for v in range(2 ** dim):
                ctrls[i].next = v
                yield delay(1)
                assert outputs[i].val == v
        raise StopSimulation

    return instances()


@myhdl_pytest(gui=True)
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
