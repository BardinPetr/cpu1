from math import log2, ceil

from myhdl import *

from machine.arch import StackCtrl
from machine.utils.hdl import *
from machine.utils.introspection import introspect


@hdl_block
def Stack(
        clk,
        in_ctrl, in_data,
        out_tos0, out_tos1,
        out_empty,
        out_full,
        depth: int,
        width: int = DATA_BITS
):
    """
    LIFO stack. Grows up from 0 to depth-1.
    DEPRECATED
    :param clk:
    :param in_ctrl:
    :param in_data:
    :param out_tos0:
    :param out_tos1:
    :param out_empty:
    :param out_full:
    :param depth:
    :param width:
    :return:
    """

    mem = [Bus(bits=width) for _ in range(depth)]
    sp = Bus(bits=ceil(log2(depth)), state=0)

    @always(clk.negedge)
    def neg():
        match in_ctrl:
            case StackCtrl.PUSH:
                if not out_full:
                    out_tos1.next = out_tos0
                    out_tos0.next = in_data
                    mem[sp].next = in_data
                    out_empty.next = 0
                    out_full.next = sp == (depth - 1)
                    sp.next = sp + 1
            case StackCtrl.POP:
                if not out_empty:
                    out_tos0.next = out_tos1
                    out_tos1.next = mem[sp - 3] if sp > 2 else 0
                    out_empty.next = sp == 1
                    out_full.next = 0
                    sp.next = sp - 1

    return introspect()
