from myhdl import *
from myhdl import _Signal

from utils.hdl import hdl_block


@hdl_block
def Trig(d_in, d_out, clk):
    @always(clk.posedge)
    def run():
        d_out.next = d_in

    return run


@hdl_block
def RTrig(d_in, d_out, clk, rst):
    @always_seq(clk.posedge, rst)
    def run():
        if rst:
            d_out.next = 0
        else:
            d_out.next = d_in

    return run


Reg = Trig
Register = Trig


@hdl_block
def Clock(clk: _Signal, period: int):
    @always(delay(period))
    def run():
        clk.next = not clk

    return run


@hdl_block
def Counter(clk: _Signal, rst: ResetSignal, out: _Signal):
    @always_seq(clk.posedge, rst)
    def run():
        if rst:
            out.next = 0
        else:
            out.next = 1 + out

    return run
