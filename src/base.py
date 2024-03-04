from myhdl import *
from myhdl import _Signal


@block
def Trig(d, q, clk):
    @always(clk.posedge)
    def run():
        q.next = d

    return run


@block
def Clock(clk: _Signal, period: int):
    @always(delay(period))
    def run():
        clk.next = not clk

    return run
