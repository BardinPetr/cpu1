from typing import List

from myhdl import *
from myhdl import _Signal

from utils.hdl import hdl_block
from utils.log import get_logger

L = get_logger()


@hdl_block
def AsyncROM(
        oe: _Signal,
        addr: _Signal,
        data: _Signal,
        contents: List[int],
        access_time: int = 5
):
    """
    Asynchronous ROM emulation component
    Outputs data from memory to data bus on OE pos front
    :param oe:       Output Enable, 1 - enable (merged with Enable)
    :param addr:     address bus
    :param data:     output data bus
    :param contents: emulated memory contents as list
    :param access_time: time to wait after OE front before changing data bus
    """

    size = len(contents)

    @instance
    def run():
        while True:
            yield oe.posedge

            _addr = int(addr.val)
            if _addr >= size:
                raise Exception(f"[ROM] Invalid address {_addr:x}")

            yield delay(access_time)  # simulate read access delay

            data.next = contents[_addr]
            L.debug(f"Accessed {_addr:x}")

            yield oe.negedge
            yield delay(1)

            data.next = 0

    return run


@hdl_block
def ROM(
        clk: _Signal,
        addr: _Signal,
        data: _Signal,
        in_contents: List[int]
):
    """
    ROM emulation component
    Outputs data from memory to data bus on OE pos front
    :param clk:      clock input, read on rising
    :param addr:     address bus
    :param data:     output data bus
    :param in_contents: emulated memory contents as list
    """

    contents = {i: v for i, v in enumerate(in_contents)}
    size = len(contents)

    @always(clk.posedge)
    def run():
        _addr = int(addr.val)
        # if _addr >= size:
        #     raise Exception(f"[ROM] Invalid address {_addr:x}")

        data.next = contents.get(_addr, 0)
        L.debug(f"Accessed {_addr:x}")

    return run
