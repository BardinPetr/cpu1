from typing import List, Optional

from myhdl import *
from myhdl import _Signal

from src.machine.utils.hdl import hdl_block, Bus
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def RAMSyncSP(
    clk: _Signal,
    wr: _Signal,
    addr: _Signal,
    in_data: _Signal,
    out_data: _Signal,
    depth: int,
    width: int,
    contents: Optional[List[int]] = None,
):
    """
    Synchronous RAM emulation component
    Read on rising clk, write when rising clk and WR
    :param clk:        clock in
    :param wr:         1 - write, 0 - no
    :param addr:       address bus
    :param in_data:    Write data bus
    :param out_data:   Read data bus
    :param width:
    :param depth:
    :param contents:
    """

    memory = [Bus(bits=width) for _ in range(depth)]

    @instance
    def init():
        if contents is not None:
            for i, v in enumerate(contents):
                memory[i].next = v
        yield None

    @always(clk.negedge)
    def write():
        if wr:
            L.info(f"WRITE [0x{int(addr.val):x}] = {in_data.val}")
            memory[addr].next = in_data

    @always(clk.posedge)
    def read():
        try:
            L.debug(f"READ [0x{int(addr.val):x}] == {memory[addr]}")
            out_data.next = memory[addr]
        except IndexError:
            out_data.next = 0

    return introspect()


@hdl_block
def RAMSyncDP(
    clk_a: _Signal,
    addr_a: _Signal,
    wr_a: _Signal,
    di_a: _Signal,
    do_a: _Signal,
    clk_b: _Signal,
    addr_b: _Signal,
    wr_b: _Signal,
    di_b: _Signal,
    do_b: _Signal,
    depth: int,
    width: int,
    contents: Optional[List[int]] = None,
):
    """
    Synchronous read-first "true"-dual-port RAM emulation component
    Read on rising clk, write when rising clk and WR
    """

    memory = [Bus(bits=width) for _ in range(depth)]

    if contents is not None:
        for i, v in enumerate(contents):
            memory[i][:] = v

    @always(clk_a.posedge)
    def write():
        do_a.next = memory[addr_a]
        if wr_a:
            memory[addr_a].next = di_a

    @always(clk_b.posedge)
    def read():
        do_b.next = memory[addr_b]
        if wr_b:
            memory[addr_b].next = di_b

    return introspect()
