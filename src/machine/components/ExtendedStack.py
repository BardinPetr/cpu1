from math import log2, ceil

from myhdl import *

from src.machine.config import DATA_BITS
from src.machine.utils.hdl import hdl_block, Bus
from src.machine.utils.introspection import introspect


@hdl_block
def ExtendedStack(
        clk,
        in_shift, in_wr_top, in_data,
        out_tos0, out_tos1,
        out_empty,
        out_full,
        depth: int,
        width: int = DATA_BITS
):
    """
    LIFO stack. Grows up from 0 to depth-1.
    :param clk:       store and move SP on falling edge
    :param in_data:   data to write
    :param in_shift:  00 - leave unchanged, 01 - push, 11 - pop
    :param in_wr_top: 1 - write to NEW TOS, 0 - no write
    :param out_tos0:  stack top - async
    :param out_tos1:  stack below top - async
    :param out_empty: stack size=0 - async
    :param out_full:  stack size=depth - async
    :param depth:     max elements in stack
    :param width:     register width
    :return:
    """

    mem = [Bus(bits=width) for _ in range(depth)]
    sp = Bus(bits=ceil(log2(depth)), state=0)

    @always_comb
    def update():
        out_tos0.next = mem[sp - 1] if sp >= 1 else 0
        out_tos1.next = mem[sp - 2] if sp >= 2 else 0
        out_full.next = sp == depth
        out_empty.next = sp == 0

    @always(clk.negedge)
    def neg():
        if (in_shift == 1 and not out_full) or \
                (in_shift == -1 and not out_empty) or \
                (in_shift == 0):
            sp.next = sp + in_shift
            if in_wr_top:
                top = sp + in_shift - 1
                mem[top].next = in_data

    return introspect()
