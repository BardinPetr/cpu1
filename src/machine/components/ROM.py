from typing import List

from myhdl import *
from myhdl import _Signal

from src.machine.utils.hdl import hdl_block
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def ROM(clk: _Signal, addr: _Signal, data: _Signal, in_contents: List[int]):
    """
    ROM emulation component
    Outputs data from memory to data bus on OE pos front
    :param clk:      clock input, read on rising
    :param addr:     address bus
    :param data:     output data bus
    :param in_contents: emulated memory contents as list
    """

    contents = {i: v for i, v in enumerate(in_contents)}

    @always(clk.posedge)
    def run():
        _addr = int(addr.val)

        data.next = contents.get(_addr, 0)
        L.debug(f"Accessed {_addr:x}")

    return introspect()
