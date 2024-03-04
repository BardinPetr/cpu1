from typing import List

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


@hdl_block
def Mux(inputs: List[_Signal], output: _Signal, ctrl: _Signal):
    @always(ctrl, *inputs)
    def run():
        output.next = inputs[int(ctrl.val)]

    return run


@hdl_block
def Clock(clk: _Signal, period: int):
    @always(delay(period))
    def run():
        clk.next = not clk

    return run
