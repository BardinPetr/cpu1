from myhdl import *

from main import Clock, Counter, Trig
from utils.testutils import myhdl_pytest


@myhdl_pytest(gui=True)
def test_counter():
    d, q, clk = [Signal(bool(0)) for _ in range(3)]

    num = Signal(intbv(0, 0, 1000))
    clock = Clock(clk, 10)
    trig = Trig(d, q, clk)
    cntr = Counter(clk, num)

    @instance
    def stimulus():
        counter = 0
        for i in range(20):
            yield clk.negedge
            counter = (counter + 1) % 11
            assert num.val._val == counter

        raise StopSimulation

    return trig, clock, stimulus, cntr
